import re
import unicodedata
from app.modules.auth.email_verification import verify_email_code
from sqlalchemy.orm import Session
import secrets
import string
import logging
from datetime import datetime, timedelta, timezone
logger = logging.getLogger(__name__)
from app.core.email import send_email
from app.modules.auth.email_templates import build_credentials_email
from app.core.security import get_password_hash
from app.modules.security.passwords.service import (
    get_active_password_policy,
    validate_password_against_policy,
)
from app.modules.security.roles.model import Permiso, RolPermiso
from app.modules.users import repository
from app.modules.users.model import Rol, Usuario
from app.modules.users.schemas import UserCreate, UserUpdate


def _normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _first_token(value: str | None) -> str:
    normalized = _normalize_text(value)
    return normalized.split(" ")[0] if normalized else ""


def _build_security_email_base(nombre: str, primer_apellido: str) -> str:
    name_token = _first_token(nombre)
    surname_token = _first_token(primer_apellido)

    if not name_token or not surname_token:
        raise ValueError("Nombre y primer apellido son obligatorios para generar el correo.")

    return f"{name_token[0]}{surname_token}"


def _generate_unique_security_email(
    db: Session,
    nombre: str,
    primer_apellido: str,
    segundo_apellido: str | None = None,
    exclude_user_id: int | None = None,
) -> str:
    base = _build_security_email_base(nombre, primer_apellido)
    second_token = _first_token(segundo_apellido)

    candidates = [f"{base}@monsterdojo.com"]
    if second_token:
        candidates.append(f"{base}{second_token[0]}@monsterdojo.com")
    for candidate in candidates:
        existing = repository.get_user_by_email(db, candidate)
        if not existing or existing.id_usuario == exclude_user_id:
            return candidate

    if second_token:
        i = 2
        while True:
            candidate = f"{base}{second_token[0]}{i}@monsterdojo.com"
            existing = repository.get_user_by_email(db, candidate)
            if not existing or existing.id_usuario == exclude_user_id:
                return candidate
            i += 1

    i = 2
    while True:
        candidate = f"{base}{i}@monsterdojo.com"
        existing = repository.get_user_by_email(db, candidate)
        if not existing or existing.id_usuario == exclude_user_id:
            return candidate
        i += 1


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    return repository.get_user_by_id(db, user_id)


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    normalized_email = email.strip().lower()
    return repository.get_user_by_email(db, normalized_email)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return repository.get_users(db, skip=skip, limit=limit)


DEFAULT_ROLE_ID = "sin_rol"
DEFAULT_ROLE_NAME = "Sin rol asignado"


def _ensure_default_role(db: Session) -> Rol:
    # Rol minimo (sin permisos) que se asigna cuando se crea un usuario sin rol.
    # Se crea bajo demanda para no acoplar el alta de usuario con la gestion de
    # roles ni depender de una migracion en la base de datos remota.
    role = repository.get_role_by_id(db, DEFAULT_ROLE_ID)
    if role:
        return role

    role = Rol(id_rol=DEFAULT_ROLE_ID, nombre=DEFAULT_ROLE_NAME, activo=True)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def _normalize_access_expiration(
    acceso_expira: bool | None,
    fecha_expiracion_acceso: datetime | None,
) -> tuple[bool, datetime | None]:
    # Devuelve (acceso_expira, fecha) ya listos para guardar.
    # - Sin expiracion: se ignora cualquier fecha enviada.
    # - Con expiracion: la fecha es obligatoria y se guarda como UTC naive
    #   (la columna remota es TIMESTAMP sin zona horaria).
    if not acceso_expira:
        return False, None

    if fecha_expiracion_acceso is None:
        raise ValueError(
            "Debes indicar la fecha de expiración del acceso cuando el acceso expira."
        )

    fecha = fecha_expiracion_acceso
    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(timezone.utc).replace(tzinfo=None)
    return True, fecha


def create_user(db: Session, user_data: UserCreate) -> Usuario:
    requested_role_id = (user_data.rol_id_rol or "").strip()

    if requested_role_id:
        role = repository.get_role_by_id(db, requested_role_id)
        if not role:
            raise ValueError("El rol especificado no existe.")
        if not role.activo:
            raise ValueError("No se puede asignar un rol inactivo.")
    else:
        # Sin rol seleccionado: se asigna un rol minimo por defecto.
        role = _ensure_default_role(db)

    policy = get_active_password_policy(db)

    # Cliente: usa su correo real como login
    if user_data.rol_id_rol == "cliente":
        if not user_data.correo:
            raise ValueError("El correo electrónico es obligatorio.")

        normalized_email = user_data.correo.strip().lower()

        if repository.exists_email_or_contact_email(db, normalized_email):
            raise ValueError("Ese correo electrónico ya está registrado.")

        verify_email_code(
            db,
            normalized_email,
            user_data.codigo_verificacion,
            commit=False,
        )

        if not user_data.password:
            raise ValueError("La contraseña es obligatoria.")

        validate_password_against_policy(user_data.password, policy)

        final_email = normalized_email
        contact_email = normalized_email
        final_password = user_data.password

    # Personal interno: correo real validado + correo institucional generado
    else:
        if not user_data.correo_contacto:
            raise ValueError("El correo de contacto es obligatorio para usuarios internos.")

        contact_email = user_data.correo_contacto.strip().lower()

        if not user_data.codigo_verificacion:
            raise ValueError("Debes verificar el correo de contacto antes de crear el usuario.")
        verify_email_code(
            db,
            contact_email,
            user_data.codigo_verificacion,
            commit=False,
        )

        # Validación mínima: el correo de contacto no debe estar repetido como contacto
        if repository.exists_email_or_contact_email(db, contact_email):
            raise ValueError("El correo de contacto ya está registrado en el sistema.")
        final_email = _generate_unique_security_email(
            db,
            nombre=user_data.nombre,
            primer_apellido=user_data.primer_apellido,
            segundo_apellido=user_data.segundo_apellido,
        )

        final_password = _generate_temporary_password()
        validate_password_against_policy(final_password, policy)

    hashed_password = get_password_hash(final_password)

    acceso_expira, fecha_expiracion_acceso = _normalize_access_expiration(
        user_data.acceso_expira,
        user_data.fecha_expiracion_acceso,
    )

    normalized_user_data = user_data.model_copy(
        update={
            "correo": final_email,
            "correo_contacto": contact_email,
            "password": final_password,
            "rol_id_rol": role.id_rol,
            "nombre": user_data.nombre.strip(),
            "primer_apellido": user_data.primer_apellido.strip(),
            "segundo_apellido": user_data.segundo_apellido.strip() if user_data.segundo_apellido else None,
            "acceso_expira": acceso_expira,
            "fecha_expiracion_acceso": fecha_expiracion_acceso,
        }
    )

    user = repository.create_user(
        db,
        normalized_user_data,
        hashed_password,
        policy.dias_expiracion,
    )

    if user.rol_id_rol != "cliente" and user_data.enviar_credenciales:
        subject, html_body, text_body = build_credentials_email(
            user.nombre,
            user.correo,
            final_password,
        )

        try:
            send_email(
                to_email=user.correo_contacto,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
            )
        except Exception:
            logger.exception(
                "Usuario creado, pero no se pudieron enviar sus credenciales. Usuario ID: %s",
                user.id_usuario,
            )

    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Usuario:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    # Resolucion del rol en edicion:
    # - None         -> no se modifica (se conserva el rol actual del usuario).
    # - "sin_rol"    -> se quita el rol y se asigna el rol minimo por defecto
    #                   (se crea bajo demanda si aun no existe).
    # - cualquier otro -> debe existir y estar activo.
    if user_data.rol_id_rol is not None:
        requested_role_id = user_data.rol_id_rol.strip()
        if requested_role_id == DEFAULT_ROLE_ID:
            role = _ensure_default_role(db)
        else:
            role = repository.get_role_by_id(db, requested_role_id)
            if not role:
                raise ValueError("El rol especificado no existe.")
            if not role.activo:
                raise ValueError("No se puede asignar un rol inactivo.")
        new_role = role.id_rol
        if new_role != user_data.rol_id_rol:
            user_data = user_data.model_copy(update={"rol_id_rol": new_role})
    else:
        new_role = user.rol_id_rol
    # clientes: correo manual y único
    if new_role == "cliente":
        if user_data.correo is not None:
            normalized_email = user_data.correo.strip().lower()
            if repository.exists_email_or_contact_email(db, normalized_email, exclude_user_id=user_id):
                raise ValueError("Ese correo electrónico ya está registrado.")
            user_data = user_data.model_copy(update={"correo": normalized_email})

    # usuarios internos: correo generado automáticamente
    else:
        nombre = user_data.nombre if user_data.nombre is not None else user.nombre
        primer_apellido = (
            user_data.primer_apellido if user_data.primer_apellido is not None else user.primer_apellido
        )
        segundo_apellido = (
            user_data.segundo_apellido if user_data.segundo_apellido is not None else user.segundo_apellido
        )

        generated_email = _generate_unique_security_email(
            db,
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            exclude_user_id=user.id_usuario,
        )

        user_data = user_data.model_copy(update={"correo": generated_email})

    # Expiracion de acceso.
    if user_data.acceso_expira is None:
        # No se modifica en esta actualizacion: se conservan los valores actuales.
        user_data = user_data.model_copy(
            update={
                "acceso_expira": user.acceso_expira,
                "fecha_expiracion_acceso": user.fecha_expiracion_acceso,
            }
        )
    elif user_data.acceso_expira:
        # Si no se envia fecha nueva, se reutiliza la que ya tiene el usuario.
        fecha = (
            user_data.fecha_expiracion_acceso
            if user_data.fecha_expiracion_acceso is not None
            else user.fecha_expiracion_acceso
        )
        acceso_expira, fecha = _normalize_access_expiration(True, fecha)
        user_data = user_data.model_copy(
            update={"acceso_expira": acceso_expira, "fecha_expiracion_acceso": fecha}
        )
    else:
        user_data = user_data.model_copy(
            update={"acceso_expira": False, "fecha_expiracion_acceso": None}
        )

    return repository.update_user(db, user, user_data)


def delete_user(db: Session, user_id: int) -> None:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    repository.delete_user(db, user)


def update_current_user(db: Session, current_user: Usuario, payload):
    if payload.nombre is not None:
        current_user.nombre = payload.nombre.strip()

    if payload.primer_apellido is not None:
        current_user.primer_apellido = payload.primer_apellido.strip()

    if payload.segundo_apellido is not None:
        current_user.segundo_apellido = payload.segundo_apellido.strip()

    if payload.correo is not None:
        normalized_email = payload.correo.strip().lower()

        if repository.exists_email_or_contact_email(
            db,
            normalized_email,
            exclude_user_id=current_user.id_usuario,
        ):
            raise ValueError("Ese correo electrónico ya está registrado.")

        current_user.correo = normalized_email
        current_user.correo_contacto = normalized_email

    if payload.telefono is not None:
        current_user.telefono = payload.telefono

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return current_user


def get_all_users(db):
    return db.query(Usuario).all()


def get_user_permissions(db: Session, user_id: int) -> list[str]:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")
#mediacion completa. comprueba permiso del usuario, estado de permiso y rol
    permisos = (
        db.query(RolPermiso.permiso_id_permiso)
        .join(
            Permiso,
            Permiso.id_permiso == RolPermiso.permiso_id_permiso,
        )
        .join(
            Rol,
            Rol.id_rol == RolPermiso.rol_id_rol,
        )
        .filter(
            RolPermiso.rol_id_rol == user.rol_id_rol,
            Rol.activo.is_(True),
            Permiso.activo.is_(True),
        )
        .all()
    )

    return [p.permiso_id_permiso for p in permisos]


def update_user_role(db: Session, user_id: int, rol_id_rol: str) -> Usuario:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    role = repository.get_role_by_id(db, rol_id_rol)
    if not role:
        raise ValueError("El rol especificado no existe.")
    if not role.activo:
        raise ValueError("No se puede asignar un rol inactivo.")

    cambia_tipo_usuario = (
        (user.rol_id_rol == "cliente" and rol_id_rol != "cliente")
        or (user.rol_id_rol != "cliente" and rol_id_rol == "cliente")
    )

    if cambia_tipo_usuario:
        raise ValueError(
            "No se puede cambiar entre cliente y personal interno desde la asignación rápida de rol. "
            "Realiza la modificación completa del usuario."
        )
    user.rol_id_rol = rol_id_rol
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user_id: int, activo: bool) -> Usuario:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    user.activo = activo
    user.is_active = activo

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def _generate_temporary_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "#$%&*"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "#$%&*" for c in password)
        ):
            return password

def get_user_by_contact_email(db: Session, email: str) -> Usuario | None:
    return repository.get_user_by_contact_email(db, email.strip().lower())


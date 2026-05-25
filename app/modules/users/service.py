import re
import unicodedata
from app.modules.auth.email_verification import verify_email_code
from sqlalchemy.orm import Session
import secrets
import string
from datetime import datetime, timedelta, timezone

from app.core.email import send_email
from app.modules.auth.email_templates import build_credentials_email
from app.core.security import get_password_hash
from app.modules.security.passwords.service import (
    get_active_password_policy,
    validate_password_against_policy,
)
from app.modules.security.roles.model import RolPermiso
from app.modules.users import repository
from app.modules.users.model import Usuario
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


def create_user(db: Session, user_data: UserCreate) -> Usuario:
    role = repository.get_role_by_id(db, user_data.rol_id_rol)
    if not role:
        raise ValueError("El rol especificado no existe.")

    policy = get_active_password_policy(db)

    # Cliente: usa su correo real como login
    if user_data.rol_id_rol == "cliente":
        if not user_data.correo:
            raise ValueError("El correo electrónico es obligatorio.")

        normalized_email = user_data.correo.strip().lower()

        existing_user = repository.get_user_by_email(db, normalized_email)
        if existing_user:
            raise ValueError("Ese correo electrónico ya está registrado.")

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
        verify_email_code(db, contact_email, user_data.codigo_verificacion)

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

    normalized_user_data = user_data.model_copy(
        update={
            "correo": final_email,
            "correo_contacto": contact_email,
            "password": final_password,
            "nombre": user_data.nombre.strip(),
            "primer_apellido": user_data.primer_apellido.strip(),
            "segundo_apellido": user_data.segundo_apellido.strip() if user_data.segundo_apellido else None,
        }
    )

    user = repository.create_user(
        db,
        normalized_user_data,
        hashed_password,
        policy.dias_expiracion,
    )

    if user.rol_id_rol != "cliente":
        subject, html_body, text_body = build_credentials_email(
            user.nombre,
            user.correo,
            final_password,
        )

        send_email(
            to_email=user.correo_contacto,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Usuario:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    new_role = user_data.rol_id_rol if user_data.rol_id_rol is not None else user.rol_id_rol

    if user_data.rol_id_rol is not None:
        role = repository.get_role_by_id(db, user_data.rol_id_rol)
        if not role:
            raise ValueError("El rol especificado no existe.")

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

    return repository.update_user(db, user, user_data)


def delete_user(db: Session, user_id: int) -> None:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    repository.delete_user(db, user)


def update_current_user(db: Session, current_user: Usuario, payload):
    current_user.nombre = payload.nombre
    current_user.primer_apellido = payload.primer_apellido
    current_user.segundo_apellido = payload.segundo_apellido
    current_user.correo = payload.correo.strip().lower()
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

    permisos = (
        db.query(RolPermiso.permiso_id_permiso)
        .filter(RolPermiso.rol_id_rol == user.rol_id_rol)
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


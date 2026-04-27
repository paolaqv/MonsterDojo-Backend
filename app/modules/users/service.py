import re
import unicodedata

from sqlalchemy.orm import Session

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

    candidates = [f"{base}.monsterdojo@gmail.com"]

    if second_token:
        candidates.append(f"{base}.{second_token[0]}.monsterdojo@gmail.com")

    for candidate in candidates:
        existing = repository.get_user_by_email(db, candidate)
        if not existing or existing.id_usuario == exclude_user_id:
            return candidate

    if second_token:
        i = 2
        while True:
            candidate = f"{base}.{second_token[0]}{i}.monsterdojo@gmail.com"
            existing = repository.get_user_by_email(db, candidate)
            if not existing or existing.id_usuario == exclude_user_id:
                return candidate
            i += 1

    i = 2
    while True:
        candidate = f"{base}{i}.monsterdojo@gmail.com"
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

    # Cliente se registra con su propio correo
    if user_data.rol_id_rol == "cliente":
        if not user_data.correo:
            raise ValueError("El correo electrónico es obligatorio.")
        normalized_email = user_data.correo.strip().lower()

        existing_user = repository.get_user_by_email(db, normalized_email)
        if existing_user:
            raise ValueError("Ese correo electrónico ya está registrado.")

        final_email = normalized_email

    # Usuarios creados por seguridad usan correo estandarizado
    else:
        final_email = _generate_unique_security_email(
            db,
            nombre=user_data.nombre,
            primer_apellido=user_data.primer_apellido,
            segundo_apellido=user_data.segundo_apellido,
        )

    policy = get_active_password_policy(db)
    validate_password_against_policy(user_data.password, policy)

    hashed_password = get_password_hash(user_data.password)

    normalized_user_data = user_data.model_copy(
        update={
            "correo": final_email,
            "nombre": user_data.nombre.strip(),
            "primer_apellido": user_data.primer_apellido.strip(),
            "segundo_apellido": user_data.segundo_apellido.strip() if user_data.segundo_apellido else None,
        }
    )

    return repository.create_user(
        db,
        normalized_user_data,
        hashed_password,
        policy.dias_expiracion,
    )


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
            existing_user = repository.get_user_by_email(db, normalized_email)

            if existing_user and existing_user.id_usuario != user.id_usuario:
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
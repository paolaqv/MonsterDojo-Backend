from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.modules.users import repository
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserCreate, UserUpdate
from app.modules.security.roles.model import RolPermiso


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    return repository.get_user_by_id(db, user_id)


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    normalized_email = email.strip().lower()
    return repository.get_user_by_email(db, normalized_email)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return repository.get_users(db, skip=skip, limit=limit)


def create_user(db: Session, user_data: UserCreate) -> Usuario:
    normalized_email = user_data.correo.strip().lower()

    existing_user = repository.get_user_by_email(db, normalized_email)
    if existing_user:
        raise ValueError("Ya existe un usuario registrado con ese correo.")

    role = repository.get_role_by_id(db, user_data.rol_id_rol)
    if not role:
        raise ValueError("El rol especificado no existe.")

    if len(user_data.password.encode("utf-8")) > 72:
        raise ValueError(
            "La contraseña no puede superar 72 bytes en UTF-8."
        )
    hashed_password = get_password_hash(user_data.password)

    normalized_user_data = user_data.model_copy(
        update={"correo": normalized_email}
    )

    return repository.create_user(db, normalized_user_data, hashed_password)


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Usuario:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    if user_data.correo is not None:
        normalized_email = user_data.correo.strip().lower()
        existing_user = repository.get_user_by_email(db, normalized_email)

        if existing_user and existing_user.id_usuario != user.id_usuario:
            raise ValueError("Ya existe un usuario registrado con ese correo.")

        user_data = user_data.model_copy(update={"correo": normalized_email})

    if user_data.rol_id_rol is not None:
        role = repository.get_role_by_id(db, user_data.rol_id_rol)
        if not role:
            raise ValueError("El rol especificado no existe.")

    return repository.update_user(db, user, user_data)


def delete_user(db: Session, user_id: int) -> None:
    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("Usuario no encontrado.")

    repository.delete_user(db, user)

def update_current_user(db, current_user: Usuario, payload):
    current_user.nombre = payload.nombre
    current_user.correo = payload.correo
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
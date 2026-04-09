from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.users.model import Rol, Usuario
from app.modules.users.schemas import UserCreate, UserUpdate


def get_role_by_id(db: Session, role_id: str) -> Rol | None:
    stmt = select(Rol).where(Rol.id_rol == role_id)
    return db.scalar(stmt)


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id_usuario == user_id)
    return db.scalar(stmt)


def get_user_by_email(db: Session, email: str) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.correo == email)
    return db.scalar(stmt)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    stmt = select(Usuario).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_user(db: Session, user_data: UserCreate, hashed_password: str) -> Usuario:
    user = Usuario(
        nombre=user_data.nombre,
        correo=user_data.correo,
        telefono=user_data.telefono,
        password=hashed_password,
        pregunta_seguridad=user_data.pregunta_seguridad,
        respuesta_seguridad=user_data.respuesta_seguridad,
        rol_id_rol=user_data.rol_id_rol,
        is_active=True,
        activo=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: Usuario, user_data: UserUpdate) -> Usuario:
    update_data = user_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user: Usuario) -> None:
    db.delete(user)
    db.commit()
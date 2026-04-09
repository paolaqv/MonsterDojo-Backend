from app.core.security import create_access_token, verify_password
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_by_email


def authenticate_user(db, email: str, password: str) -> Usuario:
    user = get_user_by_email(db, email)

    if not user:
        raise ValueError("Credenciales inválidas.")

    if not verify_password(password, user.password):
        raise ValueError("Credenciales inválidas.")

    if not user.is_active or not user.activo:
        raise ValueError("El usuario está inactivo.")

    return user


def login_user(db, email: str, password: str) -> dict:
    user = authenticate_user(db, email, password)

    access_token = create_access_token(subject=str(user.id_usuario))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }
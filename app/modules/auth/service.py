from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_by_email


def _validate_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes en UTF-8.")


def authenticate_user(db: Session, email: str, password: str) -> Usuario:
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("Credenciales inválidas.")

    if not verify_password(password, user.password):
        raise ValueError("Credenciales inválidas.")

    if not user.is_active or not user.activo:
        raise ValueError("El usuario está inactivo.")

    return user


def login_user(db: Session, email: str, password: str) -> dict:
    user = authenticate_user(db, email, password)
    access_token = create_access_token(subject=str(user.id_usuario))

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


def get_security_question(db: Session, email: str) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")

    if not user.is_active or not user.activo:
        raise ValueError("El usuario está inactivo.")

    return {
        "correo": user.correo,
        "pregunta_seguridad": user.pregunta_seguridad,
    }


def verify_security_answer(db: Session, email: str, answer: str) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")

    if user.respuesta_seguridad.strip().lower() != answer.strip().lower():
        raise ValueError("La respuesta de seguridad es incorrecta.")

    return {"message": "Respuesta de seguridad verificada correctamente."}


def reset_password_with_security_answer(
    db: Session,
    email: str,
    answer: str,
    new_password: str,
) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")

    if user.respuesta_seguridad.strip().lower() != answer.strip().lower():
        raise ValueError("La respuesta de seguridad es incorrecta.")

    _validate_password_length(new_password)
    user.password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Contraseña actualizada correctamente."}


def change_security_question(
    db: Session,
    email: str,
    password: str,
    new_question: str,
    new_answer: str,
) -> dict:
    user = authenticate_user(db, email, password)

    user.pregunta_seguridad = new_question.strip()
    user.respuesta_seguridad = new_answer.strip()

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Pregunta y respuesta de seguridad actualizadas correctamente."}
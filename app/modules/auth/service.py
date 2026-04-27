from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.email import send_email
from app.core.security import create_access_token, get_password_hash, verify_password
from app.modules.auth.email_templates import build_password_recovery_email
from app.modules.security.passwords.service import (
    apply_new_password,
    consume_password_reset_code,
    generate_password_reset_code,
    get_active_password_policy,
    verify_password_reset_code,
)
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_by_email, get_user_permissions
def _validate_password_length(password: str) -> None:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes en UTF-8.")


def authenticate_user(db: Session, email: str, password: str) -> Usuario:
    normalized_email = email.strip().lower()
    print("LOGIN EMAIL =>", normalized_email)

    user = get_user_by_email(db, normalized_email)
    policy = get_active_password_policy(db)

    print("USER FOUND =>", user.correo if user else None)

    if not user:
        print("LOGIN FAIL => usuario no encontrado")
        raise ValueError("Credenciales inválidas.")

    if not user.is_active or not user.activo:
        print("LOGIN FAIL => usuario inactivo")
        raise ValueError("El usuario está inactivo.")

    if user.bloqueado:
        print("LOGIN FAIL => usuario bloqueado")
        raise ValueError(
            "Tu cuenta está bloqueada. Debes recuperarla o contactar al encargado de seguridad."
        )

    password_ok = verify_password(password, user.password)
    print("PASSWORD MATCH =>", password_ok)
    print("HASH STORED =>", user.password)

    if not password_ok:
        user.intentos_fallidos += 1

        remaining = policy.max_intentos_login - user.intentos_fallidos

        if user.intentos_fallidos >= policy.max_intentos_login:
            user.bloqueado = True
            user.fecha_bloqueo = datetime.now(timezone.utc)
            db.add(user)
            db.commit()
            print("LOGIN FAIL => cuenta bloqueada")
            raise ValueError("Has excedido el número máximo de intentos. Tu cuenta fue bloqueada.")

        db.add(user)
        db.commit()

        if remaining == 1:
            print("LOGIN FAIL => queda un intento")
            raise ValueError(
                "Credenciales incorrectas. Advertencia: te queda 1 intento antes del bloqueo."
            )

        print("LOGIN FAIL => contraseña no coincide")
        raise ValueError("Credenciales inválidas.")

    user.intentos_fallidos = 0
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.requiere_cambio_password:
        raise ValueError("Debes cambiar tu contraseña antes de continuar.")

    if user.fecha_expiracion_password and user.fecha_expiracion_password <= datetime.now(timezone.utc):
        user.requiere_cambio_password = True
        db.add(user)
        db.commit()
        raise ValueError("Tu contraseña ha expirado. Debes cambiarla para continuar.")

    return user

def login_user(db: Session, email: str, password: str) -> dict:
    user = authenticate_user(db, email, password)
    access_token = create_access_token(subject=str(user.id_usuario))
    permisos = get_user_permissions(db, user.id_usuario)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            **user.__dict__,
            "permisos": permisos,
        },
    }


# =========================================================
# LEGACY: pregunta/respuesta de seguridad (verificacion de 2 pasos sistema antiguo)
# =========================================================

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


# =========================================================
# NUEVO: cambio obligatorio
# =========================================================

def change_password_required(
    db: Session,
    email: str,
    current_password: str,
    new_password: str,
) -> dict:
    user = get_user_by_email(db, email)
    if not user:
        raise ValueError("No existe un usuario con ese correo.")

    if not verify_password(current_password, user.password):
        raise ValueError("La contraseña actual es incorrecta.")

    apply_new_password(db, user, new_password)
    return {"message": "Contraseña actualizada correctamente. Inicia sesión nuevamente."}


# =========================================================
# NUEVO: recuperación segura por código
# =========================================================

import logging

logger = logging.getLogger(__name__)

def request_password_recovery(db: Session, email: str, app_debug: bool = False) -> dict:
    normalized_email = email.strip().lower()
    user = get_user_by_email(db, normalized_email)

    if not user:
        raise ValueError("No existe una cuenta registrada con ese correo electrónico.")

    if not user.is_active or not user.activo:
        raise ValueError("La cuenta asociada a ese correo está inactiva.")

    code = generate_password_reset_code(db, user)
    subject, html_body, text_body = build_password_recovery_email(user.nombre, code)

    try:
        logger.info("Intentando enviar código de recuperación a: %s", user.correo)

        send_email(
            to_email=user.correo,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )

        logger.info("Código de recuperación enviado correctamente a: %s", user.correo)

    except Exception as e:
        logger.exception("Error enviando correo de recuperación a %s: %s", user.correo, str(e))

        if app_debug:
            return {
                "message": "No se pudo enviar el correo real. Se generó un código de depuración.",
                "debug_code": code,
            }

        raise ValueError("No se pudo enviar el código de recuperación al correo electrónico.")

    response = {"message": "Se envió un código de recuperación al correo registrado."}

    if app_debug:
        response["debug_code"] = code

    return response

def verify_recovery_code(db: Session, email: str, code: str) -> dict:
    normalized_email = email.strip().lower()
    user = get_user_by_email(db, normalized_email)

    if not user:
        raise ValueError("No existe una cuenta registrada con ese correo electrónico.")

    verify_password_reset_code(db, user, code)
    return {"message": "Código verificado correctamente."}

def reset_password_with_code(db: Session, email: str, code: str, new_password: str) -> dict:
    normalized_email = email.strip().lower()
    user = get_user_by_email(db, normalized_email)

    if not user:
        raise ValueError("No existe una cuenta registrada con ese correo electrónico.")

    verify_password_reset_code(db, user, code)
    apply_new_password(db, user, new_password)
    consume_password_reset_code(db, user, code)

    return {"message": "Contraseña actualizada correctamente. Inicia sesión nuevamente."}
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.modules.security.passwords.model import (
    HistorialPassword,
    PasswordResetToken,
    PoliticaPassword,
)
from app.modules.users.model import Usuario


def get_active_password_policy(db: Session) -> PoliticaPassword:
    stmt = select(PoliticaPassword).where(PoliticaPassword.activa == True)
    policy = db.scalar(stmt)

    if policy:
        return policy

    now = datetime.now(timezone.utc)
    policy = PoliticaPassword(
        longitud_minima=8,
        dias_expiracion=90,
        periodo_no_reutilizacion_meses=6,
        requiere_mayusculas=True,
        requiere_minusculas=True,
        requiere_numeros=True,
        requiere_simbolos=True,
        max_intentos_login=3,
        activa=True,
        fecha_actualizacion=now,
        actualizado_por_usuario_id=None,
    )
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_password_policy(db: Session, payload, updated_by_user_id: int) -> PoliticaPassword:
    current_policy = get_active_password_policy(db)

    current_policy.longitud_minima = payload.longitud_minima
    current_policy.dias_expiracion = payload.dias_expiracion
    current_policy.periodo_no_reutilizacion_meses = payload.periodo_no_reutilizacion_meses
    current_policy.requiere_mayusculas = payload.requiere_mayusculas
    current_policy.requiere_minusculas = payload.requiere_minusculas
    current_policy.requiere_numeros = payload.requiere_numeros
    current_policy.requiere_simbolos = payload.requiere_simbolos
    current_policy.max_intentos_login = payload.max_intentos_login
    current_policy.fecha_actualizacion = datetime.now(timezone.utc)
    current_policy.actualizado_por_usuario_id = updated_by_user_id

    db.add(current_policy)

    db.execute(
        update(Usuario).values(requiere_cambio_password=True)
    )

    db.commit()
    db.refresh(current_policy)
    return current_policy


def validate_password_against_policy(password: str, policy: PoliticaPassword) -> None:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña no puede superar 72 bytes en UTF-8.")

    if len(password) < policy.longitud_minima:
        raise ValueError(
            f"La contraseña debe tener al menos {policy.longitud_minima} caracteres."
        )

    if policy.requiere_mayusculas and not any(c.isupper() for c in password):
        raise ValueError("La contraseña debe incluir al menos una letra mayúscula.")

    if policy.requiere_minusculas and not any(c.islower() for c in password):
        raise ValueError("La contraseña debe incluir al menos una letra minúscula.")

    if policy.requiere_numeros and not any(c.isdigit() for c in password):
        raise ValueError("La contraseña debe incluir al menos un número.")

    especiales = set("!@#$%^&*()_+-=[]{}|;:,.<>?/\\")
    if policy.requiere_simbolos and not any(c in especiales for c in password):
        raise ValueError("La contraseña debe incluir al menos un símbolo especial.")


def _get_security_window_start(policy: PoliticaPassword) -> datetime:
    """
    La ventana de control se basa en los días de expiración.
    Ejemplo:
    - dias_expiracion = 60
    - periodo_no_reutilizacion_meses = 6
    Significa:
      * en los últimos 60 días no puede reutilizar contraseñas usadas
      * y como máximo puede cambiar la contraseña 6 veces en esos 60 días
    """
    return datetime.now(timezone.utc) - timedelta(days=policy.dias_expiracion)


def _get_recent_password_history(
    db: Session,
    user: Usuario,
    policy: PoliticaPassword,
) -> list[HistorialPassword]:
    window_start = _get_security_window_start(policy)

    stmt = (
        select(HistorialPassword)
        .where(
            HistorialPassword.usuario_id == user.id_usuario,
            HistorialPassword.fecha_cambio >= window_start,
        )
        .order_by(HistorialPassword.fecha_cambio.desc())
    )

    return list(db.scalars(stmt).all())


def validate_password_history(
    db: Session,
    user: Usuario,
    new_password: str,
    policy: PoliticaPassword,
) -> None:
    # 1. No puede ser igual a la contraseña actual
    if verify_password(new_password, user.password):
        raise ValueError("La nueva contraseña no puede ser igual a la contraseña actual.")

    # 2. Recupera historial dentro de la vigencia actual
    recent_history = _get_recent_password_history(db, user, policy)

    # 3. No puede reutilizar ninguna contraseña usada dentro de la vigencia actual
    for item in recent_history:
        if verify_password(new_password, item.password_hash):
            raise ValueError(
                "Por seguridad, no puedes usar una contraseña reciente. Elige una contraseña nueva."
            )

    # 4. No puede exceder el máximo de cambios permitidos dentro de la vigencia actual
    #    periodo_no_reutilizacion_meses ahora se interpreta como CONTADOR, no como meses.
    max_changes_allowed = policy.periodo_no_reutilizacion_meses

    if len(recent_history) >= max_changes_allowed:
        raise ValueError(
            "Has alcanzado el número máximo de cambios de contraseña permitidos"
        )


def register_password_history(db: Session, user: Usuario) -> None:
    history = HistorialPassword(
        usuario_id=user.id_usuario,
        password_hash=user.password,
        fecha_cambio=datetime.now(timezone.utc),
    )
    db.add(history)


def apply_new_password(db: Session, user: Usuario, new_password: str) -> Usuario:
    policy = get_active_password_policy(db)

    # Valida complejidad
    validate_password_against_policy(new_password, policy)

    # Valida reutilización y contador de cambios dentro de la vigencia
    validate_password_history(db, user, new_password, policy)

    # Guarda la contraseña actual en historial antes de reemplazarla
    register_password_history(db, user)

    now = datetime.now(timezone.utc)
    user.password = get_password_hash(new_password)
    user.intentos_fallidos = 0
    user.bloqueado = False
    user.fecha_bloqueo = None
    user.requiere_cambio_password = False
    user.fecha_ultimo_cambio_password = now
    user.fecha_expiracion_password = now + timedelta(days=policy.dias_expiracion)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def unlock_user(db: Session, user: Usuario) -> Usuario:
    user.bloqueado = False
    user.intentos_fallidos = 0
    user.fecha_bloqueo = None

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _hash_reset_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def generate_password_reset_code(db: Session, user: Usuario) -> str:
    code = f"{random.randint(100000, 999999)}"

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.usuario_id == user.id_usuario,
        PasswordResetToken.usado == False,
    )
    previous_tokens = list(db.scalars(stmt).all())

    for token in previous_tokens:
        token.usado = True
        db.add(token)

    token = PasswordResetToken(
        usuario_id=user.id_usuario,
        codigo_hash=_hash_reset_code(code),
        expira_en=datetime.now(timezone.utc) + timedelta(minutes=10),
        usado=False,
        creado_en=datetime.now(timezone.utc),
    )

    db.add(token)
    db.commit()
    return code


def verify_password_reset_code(db: Session, user: Usuario, code: str) -> None:
    stmt = (
        select(PasswordResetToken)
        .where(
            PasswordResetToken.usuario_id == user.id_usuario,
            PasswordResetToken.usado == False,
        )
        .order_by(PasswordResetToken.creado_en.desc())
    )

    token = db.scalar(stmt)

    if not token:
        raise ValueError("No existe un código de recuperación vigente.")

    if token.expira_en < datetime.now(timezone.utc):
        raise ValueError("El código de recuperación ha expirado.")

    if token.codigo_hash != _hash_reset_code(code):
        raise ValueError("El código de recuperación es inválido.")


def consume_password_reset_code(db: Session, user: Usuario, code: str) -> None:
    stmt = (
        select(PasswordResetToken)
        .where(
            PasswordResetToken.usuario_id == user.id_usuario,
            PasswordResetToken.usado == False,
        )
        .order_by(PasswordResetToken.creado_en.desc())
    )

    token = db.scalar(stmt)

    if not token:
        raise ValueError("No existe un código de recuperación vigente.")

    if token.expira_en < datetime.now(timezone.utc):
        raise ValueError("El código de recuperación ha expirado.")

    if token.codigo_hash != _hash_reset_code(code):
        raise ValueError("El código de recuperación es inválido.")

    token.usado = True
    db.add(token)
    db.commit()
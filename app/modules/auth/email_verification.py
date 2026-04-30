from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy import Boolean, DateTime, Integer, String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from app.modules.users.repository import exists_email_or_contact_email
from app.core.email import send_email
from app.core.security import get_password_hash, verify_password
from app.db.base import Base
from app.modules.auth.email_templates import build_email_verification_email


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    correo: Mapped[str] = mapped_column(String(100), nullable=False)
    codigo_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def send_email_verification_code(db: Session, correo: str) -> dict:
    normalized_email = correo.strip().lower()

    if exists_email_or_contact_email(db, normalized_email):
        raise ValueError("El correo ingresado ya está registrado en el sistema.")

    code = f"{secrets.randbelow(1000000):06d}"

    token = EmailVerificationToken(
        correo=normalized_email,
        codigo_hash=get_password_hash(code),
        expira_en=datetime.now(timezone.utc) + timedelta(minutes=10),
        usado=False,
        creado_en=datetime.now(timezone.utc),
    )

    db.add(token)
    db.commit()

    subject, html_body, text_body = build_email_verification_email(code)

    send_email(
        to_email=normalized_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )

    return {"message": "Código de verificación enviado correctamente."}


def verify_email_code(db: Session, correo: str, codigo: str) -> dict:
    normalized_email = correo.strip().lower()

    stmt = (
        select(EmailVerificationToken)
        .where(func.lower(EmailVerificationToken.correo) == normalized_email)
        .where(EmailVerificationToken.usado == False)
        .order_by(EmailVerificationToken.creado_en.desc())
        .limit(1)
    )

    token = db.scalar(stmt)

    if not token:
        raise ValueError("No existe un código de verificación vigente para ese correo.")

    if token.expira_en <= datetime.now(timezone.utc):
        raise ValueError("El código de verificación expiró.")

    if not verify_password(codigo, token.codigo_hash):
        raise ValueError("El código de verificación es incorrecto.")

    token.usado = True
    db.add(token)
    db.commit()

    return {"message": "Correo verificado correctamente."}
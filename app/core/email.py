import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str | None = None) -> None:
    settings = get_settings()

    if not settings.smtp_host or not settings.smtp_from_email:
        raise ValueError(
            "El servicio de correo no está configurado. Define SMTP_HOST y SMTP_FROM_EMAIL."
        )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    if text_body:
        msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")
    else:
        msg.set_content(text_body or "Correo generado por Monster Dojo")
        msg.add_alternative(html_body, subtype="html")

    logger.info(
        "SMTP host=%s port=%s from=%s to=%s",
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_from_email,
        to_email,
    )

    if settings.smtp_use_tls:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
            if settings.smtp_user and settings.smtp_password:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
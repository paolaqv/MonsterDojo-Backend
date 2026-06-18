import base64
import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def _gmail_api_is_configured() -> bool:
    """Indica si están definidas todas las variables para usar la Gmail API."""
    settings = get_settings()
    return bool(
        settings.gmail_client_id
        and settings.gmail_client_secret
        and settings.gmail_refresh_token
        and settings.gmail_sender_email
    )


def _smtp_is_configured() -> bool:
    """Indica si están definidas las variables mínimas para usar SMTP."""
    settings = get_settings()
    return bool(settings.smtp_host and settings.smtp_from_email)


def _build_message(
    from_email: str,
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email
    message.set_content(text_body or "Correo generado por Monster Dojo.")
    message.add_alternative(html_body, subtype="html")
    return message


def _get_gmail_access_token() -> str:
    settings = get_settings()

    required_values = {
        "GMAIL_CLIENT_ID": settings.gmail_client_id,
        "GMAIL_CLIENT_SECRET": settings.gmail_client_secret,
        "GMAIL_REFRESH_TOKEN": settings.gmail_refresh_token,
    }

    missing_values = [
        variable
        for variable, value in required_values.items()
        if not value
    ]

    if missing_values:
        raise ValueError(
            "El servicio de correo no está configurado. "
            f"Faltan variables: {', '.join(missing_values)}."
        )

    try:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "refresh_token": settings.gmail_refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=20.0,
        )

        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get("access_token")

        if not access_token:
            raise RuntimeError(
                "Google no devolvió un token de acceso para enviar el correo."
            )

        return access_token

    except httpx.HTTPStatusError as error:
        logger.error(
            "Google rechazó la generación del token. Status=%s Response=%s",
            error.response.status_code,
            error.response.text,
        )
        raise RuntimeError(
            "No se pudo autorizar el servicio de correo electrónico."
        ) from error

    except httpx.RequestError as error:
        logger.error(
            "No se pudo conectar con Google OAuth: %s",
            str(error),
        )
        raise RuntimeError(
            "No se pudo conectar con el servicio de correo electrónico."
        ) from error


def _send_email_gmail_api(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> None:
    settings = get_settings()

    if not settings.gmail_sender_email:
        raise ValueError(
            "El remitente no está configurado. Define GMAIL_SENDER_EMAIL."
        )

    access_token = _get_gmail_access_token()

    message = _build_message(
        from_email=settings.gmail_sender_email,
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    try:
        logger.info(
            "Enviando correo mediante Gmail API desde %s hacia %s",
            settings.gmail_sender_email,
            to_email,
        )

        response = httpx.post(
            GMAIL_SEND_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "raw": encoded_message,
            },
            timeout=20.0,
        )

        response.raise_for_status()

        logger.info(
            "Correo enviado correctamente mediante Gmail API hacia %s",
            to_email,
        )

    except httpx.HTTPStatusError as error:
        logger.error(
            "Gmail API rechazó el envío hacia %s. Status=%s Response=%s",
            to_email,
            error.response.status_code,
            error.response.text,
        )
        raise RuntimeError(
            "No se pudo enviar el correo electrónico."
        ) from error

    except httpx.RequestError as error:
        logger.error(
            "No se pudo conectar con Gmail API para enviar correo hacia %s: %s",
            to_email,
            str(error),
        )
        raise RuntimeError(
            "No se pudo conectar con el servicio de correo electrónico."
        ) from error


def _send_email_smtp(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> None:
    settings = get_settings()

    if not settings.smtp_host or not settings.smtp_from_email:
        raise ValueError(
            "El servicio de correo no está configurado. Define SMTP_HOST y SMTP_FROM_EMAIL."
        )

    message = _build_message(
        from_email=settings.smtp_from_email,
        to_email=to_email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )

    logger.info(
        "Enviando correo mediante SMTP host=%s port=%s desde %s hacia %s",
        settings.smtp_host,
        settings.smtp_port,
        settings.smtp_from_email,
        to_email,
    )

    try:
        if settings.smtp_use_tls:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20.0) as server:
                server.starttls()
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=20.0) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(message)

        logger.info("Correo enviado correctamente mediante SMTP hacia %s", to_email)

    except smtplib.SMTPException as error:
        logger.error(
            "SMTP rechazó el envío hacia %s: %s",
            to_email,
            str(error),
        )
        raise RuntimeError(
            "No se pudo enviar el correo electrónico."
        ) from error

    except OSError as error:
        logger.error(
            "No se pudo conectar con el servidor SMTP para enviar correo hacia %s: %s",
            to_email,
            str(error),
        )
        raise RuntimeError(
            "No se pudo conectar con el servicio de correo electrónico."
        ) from error


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> None:
    """Envía un correo usando la Gmail API si está configurada; si no, usa SMTP.

    En producción se recomienda la Gmail API (HTTPS). En entornos donde solo
    están definidas las variables SMTP_*, se usa SMTP como alternativa.
    """
    if _gmail_api_is_configured():
        _send_email_gmail_api(to_email, subject, html_body, text_body)
        return

    if _smtp_is_configured():
        _send_email_smtp(to_email, subject, html_body, text_body)
        return

    raise ValueError(
        "El servicio de correo no está configurado. Define las variables GMAIL_* "
        "(GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN, GMAIL_SENDER_EMAIL) "
        "o, en su defecto, SMTP_HOST y SMTP_FROM_EMAIL."
    )

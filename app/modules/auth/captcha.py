import httpx

from app.core.config import get_settings


def verify_captcha(token: str | None, remote_ip: str | None = None) -> None:
    settings = get_settings()

    if not settings.recaptcha_secret_key:
        raise ValueError("La verificación reCAPTCHA no está configurada en el servidor.")

    if not token:
        raise ValueError("Debes completar la verificación reCAPTCHA.")

    payload = {
        "secret": settings.recaptcha_secret_key,
        "response": token,
    }

    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        response = httpx.post(
            settings.recaptcha_verify_url,
            data=payload,
            timeout=8,
        )

        response.raise_for_status()

    except httpx.HTTPError as error:
        raise ValueError("No se pudo verificar reCAPTCHA. Intenta nuevamente.")

    result = response.json()

    if not result.get("success"):
        error_codes = ", ".join(result.get("error-codes", []))
        raise ValueError(
            f"La verificación reCAPTCHA no fue válida. Detalle: {error_codes}"
        )
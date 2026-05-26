from __future__ import annotations

import re
from typing import Any


HTML_OR_SCRIPT_PATTERN = re.compile(
    r"<\s*/?\s*[a-zA-Z][^>]*>|javascript:|data:text/html|on[a-z]+\s*=",
    re.IGNORECASE,
)
CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

ROLE_ID_PATTERN = r"^[A-Za-z0-9_-]{3,50}$"
PERMISSION_ID_PATTERN = r"^[A-Za-z0-9_-]{3,60}$"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
TIME_PATTERN = r"^([01]\d|2[0-3]):[0-5]\d$"
NAME_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÜüÑñ\s]+$")
PHONE_PATTERN = re.compile(r"^\d{7,10}$")

def normalize_text(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value

    return CONTROL_CHARS_PATTERN.sub("", value).strip()


def ensure_plain_text(value: Any, field_name: str = "campo") -> Any:
    value = normalize_text(value)

    if isinstance(value, str) and HTML_OR_SCRIPT_PATTERN.search(value):
        raise ValueError(f"{field_name} no permite HTML ni scripts.")

    return value

def ensure_person_name(value: Any, field_name: str = "campo") -> Any:
    value = ensure_plain_text(value, field_name)

    if value is None:
        return value

    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} es obligatorio.")

    if not NAME_PATTERN.fullmatch(value):
        raise ValueError(f"{field_name} solo debe contener letras y espacios.")

    return value


def ensure_valid_phone(value: Any) -> Any:
    if value is None:
        return value

    if isinstance(value, bool):
        raise ValueError("El teléfono debe contener únicamente números.")

    phone = str(value).strip()

    if not PHONE_PATTERN.fullmatch(phone):
        raise ValueError("El teléfono debe tener entre 7 y 10 dígitos numéricos.")

    return int(phone)

def sanitize_plain_text(value: Any) -> Any:
    value = normalize_text(value)

    if not isinstance(value, str):
        return value

    value = HTML_OR_SCRIPT_PATTERN.sub("[contenido bloqueado]", value)
    return value.replace("<", "").replace(">", "")


def ensure_string_list(
    values: list[str] | None,
    field_name: str = "lista",
    pattern: str | None = None,
) -> list[str] | None:
    if values is None:
        return values

    cleaned: list[str] = []
    for value in values:
        normalized = ensure_plain_text(value, field_name)
        if not isinstance(normalized, str) or not normalized:
            raise ValueError(f"{field_name} contiene un valor invalido.")
        if pattern and not re.fullmatch(pattern, normalized):
            raise ValueError(f"{field_name} contiene un formato invalido.")
        cleaned.append(normalized)

    return cleaned

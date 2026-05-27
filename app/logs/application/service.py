import logging

from app.logs.application.repository import guardar_log_aplicacion
from app.shared.validation import sanitize_plain_text

logger = logging.getLogger(__name__)


SENSITIVE_WORDS = {"password", "token", "authorization", "jwt", "secret"}


def _scrub_descripcion(texto):
    if not texto:
        return texto
    lowered = texto.lower()
    for palabra in SENSITIVE_WORDS:
        if palabra in lowered:
            return "Dato sensible ocultado"
    return texto


def _coerce_entidad_id(value):
    """
    entidad_id es una columna INTEGER. Aceptamos int directo o string numérico
    para no romper a los llamadores que pasaban strings ('5', '42', etc.).
    Cualquier otra cosa (uuid, slug) cae a None para no romper la inserción.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def registrar_aplicacion(
    db,
    *,
    modulo,
    evento,
    descripcion=None,
    severidad="INFO",
    estado="OK",
    usuario_id=None,
    entidad_afectada=None,
    entidad_id=None,
):
    try:
        modulo = sanitize_plain_text(modulo)
        evento = sanitize_plain_text(evento)
        descripcion = _scrub_descripcion(sanitize_plain_text(descripcion))
        severidad = sanitize_plain_text(severidad) or "INFO"
        estado = sanitize_plain_text(estado) or "OK"
        entidad_afectada = sanitize_plain_text(entidad_afectada)
        entidad_id_safe = _coerce_entidad_id(entidad_id)

        guardar_log_aplicacion(
            db,
            {
                "modulo": modulo,
                "evento": evento,
                "descripcion": descripcion,
                "severidad": severidad,
                "estado": estado,
                "usuario_id": usuario_id,
                "entidad_afectada": entidad_afectada,
                "entidad_id": entidad_id_safe,
            },
        )
    except Exception as exc:
        logger.warning(
            "registrar_aplicacion falló: evento=%s modulo=%s | %s",
            evento,
            modulo,
            exc,
        )

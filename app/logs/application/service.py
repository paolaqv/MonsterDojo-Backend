from app.logs.application.repository import guardar_log_aplicacion
from app.shared.validation import sanitize_plain_text


SENSITIVE_WORDS = {"password", "token", "authorization", "jwt", "secret"}


def _scrub_descripcion(texto):
    if not texto:
        return texto
    lowered = texto.lower()
    for palabra in SENSITIVE_WORDS:
        if palabra in lowered:
            return "Dato sensible ocultado"
    return texto


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
        entidad_id_safe = sanitize_plain_text(str(entidad_id)) if entidad_id is not None else None

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
    except Exception:
        pass

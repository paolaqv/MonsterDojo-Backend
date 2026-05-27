import logging

from app.logs.activity.repository import guardar_log
from app.shared.validation import sanitize_plain_text

logger = logging.getLogger(__name__)


SENSITIVE_FIELDS = {
    "password",
    "token",
    "authorization",
    "jwt",
    "respuesta_seguridad",
    "secret_key",
}


def _is_sensitive_key(key) -> bool:
    normalized = str(key).lower()
    return any(field in normalized for field in SENSITIVE_FIELDS)


def _sanitize_log_value(value):
    if isinstance(value, dict):
        return {
            key: _sanitize_log_value(item)
            for key, item in value.items()
            if not _is_sensitive_key(key)
        }

    if isinstance(value, list):
        return [_sanitize_log_value(item) for item in value]

    return sanitize_plain_text(value)


def registrar_evento(
    db,
    usuario_id=None,
    rol_id=None,
    evento=None,
    modulo=None,
    accion=None,
    descripcion=None,
    ip_origen=None,
    user_agent=None,
    estado=None,
    severidad=None,
    entidad_afectada=None,
    entidad_id=None,
    valor_anterior=None,
    valor_nuevo=None,
):
    print(f"[AUDIT][registrar_evento] inicio evento={evento} modulo={modulo}", flush=True)
    try:
        evento = sanitize_plain_text(evento)
        modulo = sanitize_plain_text(modulo)
        accion = sanitize_plain_text(accion)
        descripcion = sanitize_plain_text(descripcion)
        ip_origen = sanitize_plain_text(ip_origen)
        user_agent = sanitize_plain_text(user_agent)
        estado = sanitize_plain_text(estado)
        severidad = sanitize_plain_text(severidad)
        entidad_afectada = sanitize_plain_text(entidad_afectada)
        rol_id = sanitize_plain_text(rol_id)

        if descripcion:
            texto = descripcion.lower()
            for palabra in SENSITIVE_FIELDS:
                if palabra in texto:
                    descripcion = "Dato sensible ocultado"
                    break

        print(f"[AUDIT][registrar_evento] llamando guardar_log evento={evento}", flush=True)
        resultado = guardar_log(
            db,
            {
                "usuario_id": usuario_id,
                "rol_id": rol_id,
                "evento": evento,
                "modulo": modulo,
                "accion": accion,
                "descripcion": descripcion,
                "ip_origen": ip_origen,
                "user_agent": user_agent,
                "estado": estado,
                "severidad": severidad,
                "entidad_afectada": entidad_afectada,
                "entidad_id": entidad_id,
                "valor_anterior": _sanitize_log_value(valor_anterior),
                "valor_nuevo": _sanitize_log_value(valor_nuevo),
            },
        )
        print(f"[AUDIT][registrar_evento] guardar_log retorno={resultado is not None} evento={evento}", flush=True)
    except Exception as exc:
        print(f"[AUDIT][registrar_evento] EXCEPCION evento={evento} | {type(exc).__name__}: {exc}", flush=True)
        logger.warning("registrar_evento falló: evento=%s modulo=%s | %s", evento, modulo, exc)

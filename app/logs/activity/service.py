from app.logs.activity.repository import guardar_log


SENSITIVE_FIELDS = {
    "password",
    "token",
    "authorization",
    "jwt",
    "respuesta_seguridad",
    "secret_key"
}


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
    valor_nuevo=None
):

    try:

        # -------------------------
        # A04 sanitización básica
        # -------------------------

        if descripcion:

            texto = descripcion.lower()

            for palabra in SENSITIVE_FIELDS:

                if palabra in texto:
                    descripcion = (
                        "Dato sensible ocultado"
                    )
                    break


        # opcional: evitar guardar secretos
        # dentro de JSON before/after

        if valor_anterior:
            valor_anterior = {
                k:v
                for k,v in valor_anterior.items()
                if k not in SENSITIVE_FIELDS
            }

        if valor_nuevo:
            valor_nuevo = {
                k:v
                for k,v in valor_nuevo.items()
                if k not in SENSITIVE_FIELDS
            }


        guardar_log(
            db,
            {
                "usuario_id":usuario_id,
                "rol_id":rol_id,

                "evento":evento,
                "modulo":modulo,
                "accion":accion,

                "descripcion":descripcion,

                "ip_origen":ip_origen,
                "user_agent":user_agent,

                "estado":estado,
                "severidad":severidad,

                "entidad_afectada":entidad_afectada,
                "entidad_id":entidad_id,

                "valor_anterior":valor_anterior,
                "valor_nuevo":valor_nuevo
            }
        )

    except Exception:
        pass
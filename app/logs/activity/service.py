from app.logs.activity.repository import guardar_log


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

        guardar_log(db,{
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
        })

    except Exception:
        pass
import logging

from sqlalchemy import or_, select

from app.db.session import SessionLocal
from app.logs.application.model import RegistroAplicacion

logger = logging.getLogger(__name__)


def guardar_log_aplicacion(db, data):
    """
    Inserta un evento de aplicación con SESIÓN INDEPENDIENTE.
    Si la sesión del request principal está en estado inválido
    (rollback, transacción rota), el log seguía perdiéndose en silencio.
    Una sesión propia garantiza la persistencia del evento.
    """
    log_db = SessionLocal()
    try:
        log = RegistroAplicacion(**data)
        log_db.add(log)
        log_db.commit()
        log_db.refresh(log)
        return log
    except Exception as exc:
        log_db.rollback()
        logger.warning(
            "guardar_log_aplicacion falló al insertar evento: %s | data=%s",
            exc,
            data,
        )
        return None
    finally:
        log_db.close()


def obtener_logs_aplicacion(
    db,
    *,
    severidad: str | None = None,
    search: str | None = None,
    modulo: str | None = None,
    estado: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(RegistroAplicacion)

    if severidad:
        stmt = stmt.where(RegistroAplicacion.severidad == severidad)

    if modulo:
        stmt = stmt.where(RegistroAplicacion.modulo.ilike(f"%{modulo}%"))

    if estado:
        stmt = stmt.where(RegistroAplicacion.estado == estado)

    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            or_(
                RegistroAplicacion.evento.ilike(term),
                RegistroAplicacion.modulo.ilike(term),
                RegistroAplicacion.descripcion.ilike(term),
                RegistroAplicacion.entidad_afectada.ilike(term),
            )
        )

    stmt = (
        stmt.order_by(RegistroAplicacion.fecha.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())

import logging

from sqlalchemy import or_, select

from app.db.session import SessionLocal
from app.logs.activity.model import RegistroActividad

logger = logging.getLogger(__name__)


def guardar_log(db, data):
    """
    Inserta un evento de auditoría usando una SESIÓN INDEPENDIENTE.

    Razón: si la sesión del request principal está en estado inválido
    (rollback pendiente, transacción rota, error previo), un commit ahí
    nunca persiste y el log se pierde silenciosamente.
    Una sesión propia garantiza que el evento se guarde aun cuando el
    request termine con HTTPException.
    """
    log_db = SessionLocal()
    try:
        log = RegistroActividad(**data)
        log_db.add(log)
        log_db.commit()
        log_db.refresh(log)
        return log

    except Exception as exc:
        log_db.rollback()
        logger.warning(
            "guardar_log falló al insertar evento: %s | data=%s",
            exc,
            data,
        )
        return None

    finally:
        log_db.close()


def obtener_logs(
    db,
    *,
    severidad: str | None = None,
    search: str | None = None,
    modulo: str | None = None,
    estado: str | None = None,
    critical_only: bool = False,
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(RegistroActividad)

    if critical_only:
        stmt = stmt.where(RegistroActividad.severidad.in_(["ALTA", "CRITICA"]))
    elif severidad:
        stmt = stmt.where(RegistroActividad.severidad == severidad)

    if modulo:
        stmt = stmt.where(RegistroActividad.modulo.ilike(f"%{modulo}%"))

    if estado:
        stmt = stmt.where(RegistroActividad.estado.ilike(f"%{estado}%"))

    if search:
        term = f"%{search}%"
        stmt = stmt.where(
            or_(
                RegistroActividad.evento.ilike(term),
                RegistroActividad.modulo.ilike(term),
                RegistroActividad.accion.ilike(term),
                RegistroActividad.descripcion.ilike(term),
                RegistroActividad.estado.ilike(term),
                RegistroActividad.entidad_afectada.ilike(term),
            )
        )

    stmt = (
        stmt.order_by(RegistroActividad.fecha.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(stmt).all())

from sqlalchemy import or_, select

from app.logs.application.model import RegistroAplicacion


def guardar_log_aplicacion(db, data):
    try:
        log = RegistroAplicacion(**data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
    except Exception:
        db.rollback()
        return None


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

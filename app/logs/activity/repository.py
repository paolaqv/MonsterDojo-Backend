from sqlalchemy import or_, select

from app.logs.activity.model import RegistroActividad


def guardar_log(db, data):

    try:
        log = RegistroActividad(**data)

        db.add(log)

        db.commit()

        db.refresh(log)

        return log

    except Exception:
        db.rollback()
        return None


def obtener_logs(
    db,
    *,
    severidad: str | None = None,
    search: str | None = None,
    critical_only: bool = False,
    skip: int = 0,
    limit: int = 100,
):
    stmt = select(RegistroActividad)

    if critical_only:
        stmt = stmt.where(RegistroActividad.severidad.in_(["ALTA", "CRITICA"]))
    elif severidad:
        stmt = stmt.where(RegistroActividad.severidad == severidad)

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

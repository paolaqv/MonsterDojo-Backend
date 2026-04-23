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


def obtener_logs(db):

    return (
        db.query(
            RegistroActividad
        )
        .order_by(
            RegistroActividad.fecha.desc()
        )
        .all()
    )
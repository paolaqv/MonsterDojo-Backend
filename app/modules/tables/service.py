from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.modules.reservations.model import Reserva
from app.modules.tables import repository
from app.modules.tables.model import Mesa
from app.modules.tables.schemas import TableCreate, TableUpdate


def get_table_by_id(db: Session, table_id: int) -> Mesa | None:
    return repository.get_table_by_id(db, table_id)


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> list[Mesa]:
    return repository.get_tables(db, skip=skip, limit=limit)


def create_table(db: Session, table_data: TableCreate) -> Mesa:
    return repository.create_table(db, table_data)


def update_table(db: Session, table_id: int, table_data: TableUpdate) -> Mesa:
    table = repository.get_table_by_id(db, table_id)
    if not table:
        raise ValueError("Mesa no encontrada.")

    return repository.update_table(db, table, table_data)

MAX_RESERVATION_DURATION = timedelta(hours=2, minutes=30)


def get_available_tables(
    db: Session,
        *,
        fecha: str,
        hora_inicio: str,
        hora_fin: str,
        usuario_id: int,
        exclude_reservation_id: int | None = None,
):
    try:
        fecha_hora_inicio = datetime.strptime(f"{fecha} {hora_inicio}", "%Y-%m-%d %H:%M")
        fecha_hora_fin = datetime.strptime(f"{fecha} {hora_fin}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise ValueError("Formato de fecha u hora inválido.")

    if fecha_hora_fin <= fecha_hora_inicio:
        raise ValueError("La hora de fin debe ser mayor que la hora de inicio.")

    if (fecha_hora_fin - fecha_hora_inicio) > MAX_RESERVATION_DURATION:
        raise ValueError("La reserva no puede exceder 2 horas y 30 minutos.")

    reservas_usuario = (
        db.query(Reserva)
        .filter(
            Reserva.usuario_id_usuario == usuario_id,
            Reserva.estado != "Cancelado",
        )
        .all()
    )

    for reserva in reservas_usuario:
        if exclude_reservation_id is not None and reserva.id_reserva == exclude_reservation_id:
            continue

        if reserva.fecha_hora.date() == fecha_hora_inicio.date():
            raise ValueError("Elige otra fecha, ya tienes una reserva en esta fecha.")
    mesas = (
        db.query(Mesa)
        .filter((Mesa.activo == True) | (Mesa.activo.is_(None)))
        .all()
    )

    mesas_disponibles = []

    for mesa in mesas:
        reservas_mesa = (
            db.query(Reserva)
            .filter(
                Reserva.mesa_id_mesa == mesa.id_mesa,
                Reserva.estado != "Cancelado",
            )
            .all()
        )

        reserva_solapada = None
        for reserva in reservas_mesa:
            inicio_existente = reserva.fecha_hora
            fin_existente = reserva.fecha_hora + MAX_RESERVATION_DURATION

            hay_solapamiento = (
                inicio_existente < fecha_hora_fin and
                fin_existente > fecha_hora_inicio
            )

            if hay_solapamiento:
                reserva_solapada = reserva
                break

        if reserva_solapada:
            proxima_disponibilidad = reserva_solapada.fecha_hora + MAX_RESERVATION_DURATION
            mesas_disponibles.append({
                "mesa": {
                    "id_mesa": mesa.id_mesa,
                    "capacidad": mesa.capacidad,
                    "ubicacion": mesa.ubicacion,
                },
                "disponible": False,
                "proxima_disponibilidad": proxima_disponibilidad,
            })
        else:
            mesas_disponibles.append({
                "mesa": {
                    "id_mesa": mesa.id_mesa,
                    "capacidad": mesa.capacidad,
                    "ubicacion": mesa.ubicacion,
                },
                "disponible": True,
                "proxima_disponibilidad": None,
            })

    return mesas_disponibles

def archive_table(db: Session, table_id: int) -> Mesa:
    mesa = repository.get_table_by_id(db, table_id)
    if not mesa:
        raise ValueError("Mesa no encontrada.")

    return repository.archive_table(db, mesa)


def unarchive_table(db: Session, table_id: int) -> Mesa:
    mesa = repository.get_table_by_id(db, table_id)
    if not mesa:
        raise ValueError("Mesa no encontrada.")

    return repository.unarchive_table(db, mesa)
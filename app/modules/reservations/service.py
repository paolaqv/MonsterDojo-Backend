from sqlalchemy.orm import Session

from app.modules.reservations import repository
from app.modules.reservations.model import DetalleReserva, Reserva
from app.modules.reservations.schemas import (
    ReservationCreate,
    ReservationDetailCreate,
    ReservationUpdate,
)


def get_reservation_by_id(db: Session, reservation_id: int) -> Reserva | None:
    return repository.get_reservation_by_id(db, reservation_id)


def get_reservations(db: Session, skip: int = 0, limit: int = 100) -> list[Reserva]:
    return repository.get_reservations(db, skip=skip, limit=limit)


def create_reservation(db: Session, reservation_data: ReservationCreate) -> Reserva:
    user = repository.get_user_by_id(db, reservation_data.usuario_id_usuario)
    if not user:
        raise ValueError("El usuario no existe.")

    table = repository.get_table_by_id(db, reservation_data.mesa_id_mesa)
    if not table:
        raise ValueError("La mesa no existe.")

    return repository.create_reservation(db, reservation_data)


def update_reservation(
    db: Session,
    reservation_id: int,
    reservation_data: ReservationUpdate,
) -> Reserva:
    reservation = repository.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("Reserva no encontrada.")

    if reservation_data.usuario_id_usuario is not None:
        user = repository.get_user_by_id(db, reservation_data.usuario_id_usuario)
        if not user:
            raise ValueError("El usuario no existe.")

    if reservation_data.mesa_id_mesa is not None:
        table = repository.get_table_by_id(db, reservation_data.mesa_id_mesa)
        if not table:
            raise ValueError("La mesa no existe.")

    return repository.update_reservation(db, reservation, reservation_data)


def get_reservation_detail_by_id(db: Session, detail_id: int) -> DetalleReserva | None:
    return repository.get_reservation_detail_by_id(db, detail_id)


def get_reservation_details_by_reservation_id(
    db: Session,
    reservation_id: int,
) -> list[DetalleReserva]:
    reservation = repository.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("Reserva no encontrada.")

    return repository.get_reservation_details_by_reservation_id(db, reservation_id)


def create_reservation_detail(
    db: Session,
    detail_data: ReservationDetailCreate,
) -> DetalleReserva:
    reservation = repository.get_reservation_by_id(db, detail_data.reserva_id_reserva)
    if not reservation:
        raise ValueError("La reserva no existe.")

    product = repository.get_product_by_id(db, detail_data.producto_id_producto)
    if not product:
        raise ValueError("El producto no existe.")

    return repository.create_reservation_detail(db, detail_data)
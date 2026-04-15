from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products.model import Producto
from app.modules.reservations.model import DetalleReserva, Reserva
from app.modules.reservations.schemas import (
    ReservationCreate,
    ReservationDetailCreate,
    ReservationUpdate,
)
from app.modules.tables.model import Mesa
from app.modules.users.model import Usuario


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id_usuario == user_id)
    return db.scalar(stmt)


def get_table_by_id(db: Session, table_id: int) -> Mesa | None:
    stmt = select(Mesa).where(Mesa.id_mesa == table_id)
    return db.scalar(stmt)


def get_product_by_id(db: Session, product_id: int) -> Producto | None:
    stmt = select(Producto).where(Producto.id_producto == product_id)
    return db.scalar(stmt)


def get_reservation_by_id(db: Session, reservation_id: int) -> Reserva | None:
    stmt = select(Reserva).where(Reserva.id_reserva == reservation_id)
    return db.scalar(stmt)


def get_reservations(db: Session, skip: int = 0, limit: int = 100) -> list[Reserva]:
    stmt = select(Reserva).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_reservation(db: Session, reservation_data: ReservationCreate) -> Reserva:
    reservation = Reserva(
        fecha_hora=reservation_data.fecha_hora,
        estado=reservation_data.estado,
        usuario_id_usuario=reservation_data.usuario_id_usuario,
        mesa_id_mesa=reservation_data.mesa_id_mesa,
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def update_reservation(db: Session, reservation: Reserva, reservation_data: ReservationUpdate) -> Reserva:
    update_data = reservation_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(reservation, field, value)

    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_reservation_detail_by_id(db: Session, detail_id: int) -> DetalleReserva | None:
    stmt = select(DetalleReserva).where(DetalleReserva.id_detalleReserva == detail_id)
    return db.scalar(stmt)


def get_reservation_details_by_reservation_id(
    db: Session,
    reservation_id: int,
) -> list[DetalleReserva]:
    stmt = select(DetalleReserva).where(
        DetalleReserva.reserva_id_reserva == reservation_id
    )
    return list(db.scalars(stmt).all())


def create_reservation_detail(
    db: Session,
    detail_data: ReservationDetailCreate,
) -> DetalleReserva:
    detail = DetalleReserva(
        cantidad=detail_data.cantidad,
        precio=detail_data.precio,
        producto_id_producto=detail_data.producto_id_producto,
        reserva_id_reserva=detail_data.reserva_id_reserva,
    )

    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail
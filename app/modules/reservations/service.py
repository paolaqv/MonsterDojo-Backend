# app/modules/reservations/service.py

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.game_rentals.model import RegistroJuego
from app.modules.games.model import Juego
from app.modules.products.model import Producto
from app.modules.reservations import repository
from app.modules.reservations.model import DetalleReserva, Reserva
from app.modules.reservations.schemas import (
    ReservationCreate,
    ReservationDetailCreate,
    ReservationUpdate,
)
from app.modules.tables.service import get_available_tables

RESERVATION_ALLOWED_TRANSITIONS = {
    "Reservado": {"Cancelado", "Finalizado"},
    "Cancelado": set(),
    "Finalizado": set(),
}


def get_reservation_by_id(db: Session, reservation_id: int) -> Reserva | None:
    return repository.get_reservation_by_id(db, reservation_id)


def get_reservation_by_id_admin(db: Session, reservation_id: int) -> Reserva | None:
    return repository.get_reservation_by_id(db, reservation_id)


def get_active_reservation_for_user(db: Session, user_id: int) -> Reserva | None:
    return repository.get_active_reservation_by_user_id(db, user_id)


def get_reservations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int | None = None,
) -> list[Reserva]:
    return repository.get_reservations(db, skip=skip, limit=limit, user_id=user_id)


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

    if reservation_data.estado is not None and reservation_data.estado != reservation.estado:
        allowed_next_states = RESERVATION_ALLOWED_TRANSITIONS.get(reservation.estado, set())

        if reservation_data.estado not in allowed_next_states:
            raise ValueError(
                "Transicion de estado de reserva no permitida: "
                f"{reservation.estado} -> {reservation_data.estado}."
            )

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


def get_reservation_details_by_reservation_id_admin(
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


def create_reservation_checkout(
    db: Session,
    *,
    payload,
    current_user,
):
    available_tables = get_available_tables(
        db,
        fecha=payload.date,
        hora_inicio=payload.start_time,
        hora_fin=payload.end_time,
        usuario_id=current_user.id_usuario,
    )

    mesa_info = next(
        (item for item in available_tables if item["mesa"]["id_mesa"] == payload.mesa_id),
        None,
    )

    if not mesa_info:
        raise ValueError("La mesa seleccionada no existe.")

    if not mesa_info["disponible"]:
        raise ValueError("La mesa seleccionada no está disponible en ese horario.")

    fecha_hora_inicio = datetime.strptime(
        f"{payload.date} {payload.start_time}",
        "%Y-%m-%d %H:%M",
    )

    reserva = Reserva(
        fecha_hora=fecha_hora_inicio,
        estado="Reservado",
        usuario_id_usuario=current_user.id_usuario,
        mesa_id_mesa=payload.mesa_id,
    )

    try:
        db.add(reserva)
        db.flush()

        for item in payload.productos:
            producto = db.get(Producto, item.id_producto)
            if not producto:
                raise ValueError(f"No existe el producto con id {item.id_producto}.")

            detalle_reserva = DetalleReserva(
                cantidad=item.cantidad,
                precio=producto.precio,
                producto_id_producto=item.id_producto,
                reserva_id_reserva=reserva.id_reserva,
            )
            db.add(detalle_reserva)

        if payload.juego_id:
            juego = db.get(Juego, payload.juego_id)
            if not juego:
                raise ValueError(f"No existe el juego con id {payload.juego_id}.")

            registro_juego = RegistroJuego(
                cantidad=1,
                precio=juego.precio_alquiler,
                tipo=1,
                juego_id_juego=payload.juego_id,
                usuario_id_usuario=current_user.id_usuario,
                reserva_id_reserva=reserva.id_reserva,
            )
            db.add(registro_juego)

        db.commit()
        db.refresh(reserva)

        return {
            "message": "Reserva confirmada con éxito.",
            "id_reserva": reserva.id_reserva,
        }

    except Exception:
        db.rollback()
        raise


def update_reservation_checkout(
    db: Session,
    *,
    reservation_id: int,
    payload,
    current_user,
):
    reserva = repository.get_reservation_by_id(db, reservation_id)
    if not reserva:
        raise ValueError("Reserva no encontrada.")

    if reserva.usuario_id_usuario != current_user.id_usuario:
        raise ValueError("No tienes permiso para modificar esta reserva.")

    if reserva.estado != "Reservado":
        raise ValueError("Solo se pueden modificar reservas activas.")

    available_tables = get_available_tables(
        db,
        fecha=payload.date,
        hora_inicio=payload.start_time,
        hora_fin=payload.end_time,
        usuario_id=current_user.id_usuario,
        exclude_reservation_id=reservation_id,
    )
    mesa_info = next(
        (item for item in available_tables if item["mesa"]["id_mesa"] == payload.mesa_id),
        None,
    )

    if not mesa_info:
        raise ValueError("La mesa seleccionada no existe.")

    misma_mesa = reserva.mesa_id_mesa == payload.mesa_id
    if not mesa_info["disponible"] and not misma_mesa:
        raise ValueError("La mesa seleccionada no está disponible en ese horario.")

    fecha_hora_inicio = datetime.strptime(
        f"{payload.date} {payload.start_time}",
        "%Y-%m-%d %H:%M",
    )

    try:
        reserva.fecha_hora = fecha_hora_inicio
        reserva.mesa_id_mesa = payload.mesa_id
        reserva.estado = "Reservado"

        repository.delete_reservation_details_by_reservation_id(db, reserva.id_reserva)
        repository.delete_game_rental_by_reservation_id(db, reserva.id_reserva)

        for item in payload.productos:
            producto = db.get(Producto, item.id_producto)
            if not producto:
                raise ValueError(f"No existe el producto con id {item.id_producto}.")

            detalle_reserva = DetalleReserva(
                cantidad=item.cantidad,
                precio=producto.precio,
                producto_id_producto=item.id_producto,
                reserva_id_reserva=reserva.id_reserva,
            )
            db.add(detalle_reserva)

        if payload.juego_id:
            juego = db.get(Juego, payload.juego_id)
            if not juego:
                raise ValueError(f"No existe el juego con id {payload.juego_id}.")

            registro_juego = RegistroJuego(
                cantidad=1,
                precio=juego.precio_alquiler,
                tipo=1,
                juego_id_juego=payload.juego_id,
                usuario_id_usuario=current_user.id_usuario,
                reserva_id_reserva=reserva.id_reserva,
            )
            db.add(registro_juego)

        db.commit()
        db.refresh(reserva)

        return {
            "message": "Reserva actualizada con éxito.",
            "id_reserva": reserva.id_reserva,
        }

    except Exception:
        db.rollback()
        raise

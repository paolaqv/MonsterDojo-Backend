from sqlalchemy.orm import Session

from app.modules.payments import repository
from app.modules.payments.model import Pago
from app.modules.payments.schemas import PaymentCreate, PaymentUpdate


def get_payment_by_id(db: Session, payment_id: int) -> Pago | None:
    return repository.get_payment_by_id(db, payment_id)


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> list[Pago]:
    return repository.get_payments(db, skip=skip, limit=limit)


def create_payment(db: Session, payment_data: PaymentCreate) -> Pago:
    user = repository.get_user_by_id(db, payment_data.usuario_id_usuario)
    if not user:
        raise ValueError("El usuario no existe.")

    order_detail = repository.get_order_detail_by_id(
        db, payment_data.detalle_pedido_id_detallePed
    )
    if not order_detail:
        raise ValueError("El detalle de pedido no existe.")

    reservation_detail = repository.get_reservation_detail_by_id(
        db, payment_data.detalle_reserva_id_detalleReserva
    )
    if not reservation_detail:
        raise ValueError("El detalle de reserva no existe.")

    game_rental = repository.get_game_rental_by_id(
        db, payment_data.registro_juego_id_regJuego
    )
    if not game_rental:
        raise ValueError("El registro de juego no existe.")
    if order_detail.pedido_rel.usuario_id_usuario != payment_data.usuario_id_usuario:
        raise ValueError("El detalle de pedido no corresponde al usuario indicado.")

    if reservation_detail.reserva_rel.usuario_id_usuario != payment_data.usuario_id_usuario:
        raise ValueError("El detalle de reserva no corresponde al usuario indicado.")

    if game_rental.usuario_id_usuario != payment_data.usuario_id_usuario:
        raise ValueError("El registro de juego no corresponde al usuario indicado.")

    if game_rental.reserva_id_reserva != reservation_detail.reserva_id_reserva:
        raise ValueError("El juego y el detalle no corresponden a la misma reserva.")

    return repository.create_payment(db, payment_data)


def update_payment(db: Session, payment_id: int, payment_data: PaymentUpdate) -> Pago:
    payment = repository.get_payment_by_id(db, payment_id)
    if not payment:
        raise ValueError("Pago no encontrado.")

    user_id = (
        payment_data.usuario_id_usuario
        if payment_data.usuario_id_usuario is not None
        else payment.usuario_id_usuario
    )
    order_detail_id = (
        payment_data.detalle_pedido_id_detallePed
        if payment_data.detalle_pedido_id_detallePed is not None
        else payment.detalle_pedido_id_detallePed
    )
    reservation_detail_id = (
        payment_data.detalle_reserva_id_detalleReserva
        if payment_data.detalle_reserva_id_detalleReserva is not None
        else payment.detalle_reserva_id_detalleReserva
    )
    game_rental_id = (
        payment_data.registro_juego_id_regJuego
        if payment_data.registro_juego_id_regJuego is not None
        else payment.registro_juego_id_regJuego
    )

    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("El usuario no existe.")

    order_detail = repository.get_order_detail_by_id(db, order_detail_id)
    if not order_detail:
        raise ValueError("El detalle de pedido no existe.")

    reservation_detail = repository.get_reservation_detail_by_id(db, reservation_detail_id)
    if not reservation_detail:
        raise ValueError("El detalle de reserva no existe.")

    game_rental = repository.get_game_rental_by_id(db, game_rental_id)
    if not game_rental:
        raise ValueError("El registro de juego no existe.")

    if order_detail.pedido_rel.usuario_id_usuario != user_id:
        raise ValueError("El detalle de pedido no corresponde al usuario indicado.")

    if reservation_detail.reserva_rel.usuario_id_usuario != user_id:
        raise ValueError("El detalle de reserva no corresponde al usuario indicado.")

    if game_rental.usuario_id_usuario != user_id:
        raise ValueError("El registro de juego no corresponde al usuario indicado.")

    if game_rental.reserva_id_reserva != reservation_detail.reserva_id_reserva:
        raise ValueError("El juego y el detalle no corresponden a la misma reserva.")

    return repository.update_payment(db, payment, payment_data)
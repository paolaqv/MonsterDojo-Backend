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

    return repository.create_payment(db, payment_data)


def update_payment(db: Session, payment_id: int, payment_data: PaymentUpdate) -> Pago:
    payment = repository.get_payment_by_id(db, payment_id)
    if not payment:
        raise ValueError("Pago no encontrado.")

    if payment_data.usuario_id_usuario is not None:
        user = repository.get_user_by_id(db, payment_data.usuario_id_usuario)
        if not user:
            raise ValueError("El usuario no existe.")

    if payment_data.detalle_pedido_id_detallePed is not None:
        order_detail = repository.get_order_detail_by_id(
            db, payment_data.detalle_pedido_id_detallePed
        )
        if not order_detail:
            raise ValueError("El detalle de pedido no existe.")

    if payment_data.detalle_reserva_id_detalleReserva is not None:
        reservation_detail = repository.get_reservation_detail_by_id(
            db, payment_data.detalle_reserva_id_detalleReserva
        )
        if not reservation_detail:
            raise ValueError("El detalle de reserva no existe.")

    if payment_data.registro_juego_id_regJuego is not None:
        game_rental = repository.get_game_rental_by_id(
            db, payment_data.registro_juego_id_regJuego
        )
        if not game_rental:
            raise ValueError("El registro de juego no existe.")

    return repository.update_payment(db, payment, payment_data)
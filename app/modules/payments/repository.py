from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.game_rentals.model import RegistroJuego
from app.modules.orders.model import DetallePedido
from app.modules.payments.model import Pago
from app.modules.payments.schemas import PaymentCreate, PaymentUpdate
from app.modules.reservations.model import DetalleReserva
from app.modules.users.model import Usuario


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id_usuario == user_id)
    return db.scalar(stmt)


def get_order_detail_by_id(db: Session, detail_id: int) -> DetallePedido | None:
    stmt = select(DetallePedido).where(DetallePedido.id_detallePed == detail_id)
    return db.scalar(stmt)


def get_reservation_detail_by_id(db: Session, detail_id: int) -> DetalleReserva | None:
    stmt = select(DetalleReserva).where(DetalleReserva.id_detalleReserva == detail_id)
    return db.scalar(stmt)


def get_game_rental_by_id(db: Session, rental_id: int) -> RegistroJuego | None:
    stmt = select(RegistroJuego).where(RegistroJuego.id_regJuego == rental_id)
    return db.scalar(stmt)


def get_payment_by_id(db: Session, payment_id: int) -> Pago | None:
    stmt = select(Pago).where(Pago.id_pago == payment_id)
    return db.scalar(stmt)


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> list[Pago]:
    stmt = select(Pago).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_payment(db: Session, payment_data: PaymentCreate) -> Pago:
    payment = Pago(
        fecha=payment_data.fecha,
        monto=payment_data.monto,
        detalle_pedido_id_detallePed=payment_data.detalle_pedido_id_detallePed,
        detalle_reserva_id_detalleReserva=payment_data.detalle_reserva_id_detalleReserva,
        registro_juego_id_regJuego=payment_data.registro_juego_id_regJuego,
        usuario_id_usuario=payment_data.usuario_id_usuario,
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def update_payment(db: Session, payment: Pago, payment_data: PaymentUpdate) -> Pago:
    update_data = payment_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(payment, field, value)

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment
# app/modules/orders/service.py

from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.orders import repository
from app.modules.orders.model import DetallePedido, Pedido
from app.modules.orders.schemas import OrderCreate, OrderDetailCreate, OrderUpdate


def get_order_by_id(db: Session, order_id: int) -> Pedido | None:
    return repository.get_order_by_id(db, order_id)


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> list[Pedido]:
    return repository.get_orders(db, skip=skip, limit=limit)


def create_order(db: Session, order_data: OrderCreate, current_user) -> Pedido:
    reserva_activa = repository.get_active_reservation_by_user_id(db, current_user.id_usuario)
    if not reserva_activa:
        raise ValueError("No tienes una reserva activa.")

    try:
        order = repository.create_order(
            db,
            tipo="Pedido",
            estado="Pendiente",
            fecha_hora=datetime.utcnow(),
            usuario_id_usuario=current_user.id_usuario,
            mesa_id_mesa=reserva_activa.mesa_id_mesa,
        )

        for item in order_data.productos:
            product = repository.get_product_by_id(db, item.id_producto)
            if not product:
                raise ValueError(f"No existe el producto con id {item.id_producto}.")

            detail = OrderDetailCreate(
                cantidad=item.cantidad,
                precio=product.precio,
                producto_id_producto=item.id_producto,
                pedido_id_pedido=order.id_pedido,
            )
            repository.create_order_detail(db, detail)

        db.commit()
        db.refresh(order)
        return order
    except Exception:
        db.rollback()
        raise


def update_order(db: Session, order_id: int, order_data: OrderUpdate) -> Pedido:
    order = repository.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Pedido no encontrado.")

    if order_data.usuario_id_usuario is not None:
        user = repository.get_user_by_id(db, order_data.usuario_id_usuario)
        if not user:
            raise ValueError("El usuario no existe.")

    if order_data.mesa_id_mesa is not None:
        table = repository.get_table_by_id(db, order_data.mesa_id_mesa)
        if not table:
            raise ValueError("La mesa no existe.")

    return repository.update_order(db, order, order_data)


def get_order_detail_by_id(db: Session, detail_id: int) -> DetallePedido | None:
    return repository.get_order_detail_by_id(db, detail_id)


def get_order_details_by_order_id(db: Session, order_id: int) -> list[DetallePedido]:
    order = repository.get_order_by_id(db, order_id)
    if not order:
        raise ValueError("Pedido no encontrado.")

    return repository.get_order_details_by_order_id(db, order_id)


def create_order_detail(db: Session, detail_data: OrderDetailCreate) -> DetallePedido:
    order = repository.get_order_by_id(db, detail_data.pedido_id_pedido)
    if not order:
        raise ValueError("El pedido no existe.")

    product = repository.get_product_by_id(db, detail_data.producto_id_producto)
    if not product:
        raise ValueError("El producto no existe.")

    detail = repository.create_order_detail(db, detail_data)
    db.commit()
    db.refresh(detail)
    return detail
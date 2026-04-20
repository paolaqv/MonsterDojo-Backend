# app/modules/orders/repository.py

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.orders.model import DetallePedido, Pedido
from app.modules.orders.schemas import OrderDetailCreate, OrderUpdate
from app.modules.products.model import Producto
from app.modules.reservations.model import Reserva
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


def get_order_by_id(db: Session, order_id: int) -> Pedido | None:
    stmt = select(Pedido).where(Pedido.id_pedido == order_id)
    return db.scalar(stmt)


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> list[Pedido]:
    stmt = select(Pedido).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_active_reservation_by_user_id(db: Session, user_id: int) -> Reserva | None:
    stmt = (
        select(Reserva)
        .where(
            Reserva.usuario_id_usuario == user_id,
            Reserva.estado == "Reservado",
        )
        .order_by(Reserva.fecha_hora.desc())
    )
    return db.scalar(stmt)


def create_order(
    db: Session,
    *,
    tipo: str,
    estado: str,
    fecha_hora,
    usuario_id_usuario: int,
    mesa_id_mesa: int,
) -> Pedido:
    order = Pedido(
        tipo=tipo,
        estado=estado,
        fecha_hora=fecha_hora,
        usuario_id_usuario=usuario_id_usuario,
        mesa_id_mesa=mesa_id_mesa,
    )

    db.add(order)
    db.flush()
    return order


def update_order(db: Session, order: Pedido, order_data: OrderUpdate) -> Pedido:
    update_data = order_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(order, field, value)

    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order_detail_by_id(db: Session, detail_id: int) -> DetallePedido | None:
    stmt = select(DetallePedido).where(DetallePedido.id_detallePed == detail_id)
    return db.scalar(stmt)


def get_order_details_by_order_id(db: Session, order_id: int) -> list[DetallePedido]:
    stmt = select(DetallePedido).where(DetallePedido.pedido_id_pedido == order_id)
    return list(db.scalars(stmt).all())


def create_order_detail(
    db: Session,
    detail_data: OrderDetailCreate,
) -> DetallePedido:
    detail = DetallePedido(
        cantidad=detail_data.cantidad,
        precio=detail_data.precio,
        producto_id_producto=detail_data.producto_id_producto,
        pedido_id_pedido=detail_data.pedido_id_pedido,
    )

    db.add(detail)
    db.flush()
    return detail
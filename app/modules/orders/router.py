from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.application.service import registrar_aplicacion
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.permissions import (
    require_any_permission,
    require_permissions,
    user_has_any_permission,
)
from app.modules.orders.schemas import (
    OrderCreate,
    OrderDetailCreate,
    OrderDetailRead,
    OrderRead,
    OrderUpdate,
)
from app.modules.orders.service import (
    create_order,
    create_order_detail,
    get_order_by_id,
    get_order_detail_by_id,
    get_order_details_by_order_id,
    get_orders,
    update_order,
)
from app.modules.users.model import Usuario

router = APIRouter(prefix="/orders", tags=["Orders"])


def _can_view_all_orders(db: Session, current_user: Usuario) -> bool:
    return user_has_any_permission(
        db,
        current_user,
        "ver_pedidos_detalle",
        "gestionar_pedidos",
    )


@router.get("/", response_model=list[OrderRead])
def read_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    orders = get_orders(db, skip=skip, limit=limit)

    if _can_view_all_orders(db, current_user):
        return orders

    return [order for order in orders if order.usuario_id_usuario == current_user.id_usuario]


@router.get("/{order_id}", response_model=OrderRead)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado.",
        )

    if not _can_view_all_orders(db, current_user) and order.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pedido.",
        )

    return order


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_new_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_any_permission("crear_pedidos", "gestionar_pedidos")
    ),
):
    try:
        order = create_order(db, payload, current_user)

        registrar_aplicacion(
            db,
            modulo="pedidos",
            evento="PEDIDO_CREADO",
            descripcion=f"Usuario {current_user.id_usuario} creo pedido {order.id_pedido} en mesa {order.mesa_id_mesa}.",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="pedido",
            entidad_id=order.id_pedido,
        )

        return order
    except ValueError as e:
        registrar_aplicacion(
            db,
            modulo="pedidos",
            evento="PEDIDO_RECHAZADO",
            descripcion=str(e),
            severidad="WARN",
            estado="FAIL",
            usuario_id=current_user.id_usuario,
            entidad_afectada="pedido",
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{order_id}", response_model=OrderRead)
def update_existing_order(
    order_id: int,
    payload: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permissions("gestionar_pedidos")),
):
    order_before = get_order_by_id(db, order_id)
    old_state = order_before.estado if order_before else None

    try:
        order = update_order(db, order_id, payload)

        if payload.estado is not None and payload.estado != old_state:
            registrar_aplicacion(
                db,
                modulo="pedidos",
                evento="PEDIDO_ESTADO_CAMBIADO",
                descripcion=f"Pedido {order_id} cambio de '{old_state}' a '{payload.estado}' (usuario {current_user.id_usuario}).",
                severidad="INFO" if payload.estado != "Cancelado" else "WARN",
                estado="OK",
                usuario_id=current_user.id_usuario,
                entidad_afectada="pedido",
                entidad_id=order_id,
            )

        return order
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Pedido no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )


@router.get("/{order_id}/details", response_model=list[OrderDetailRead])
def read_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    order = get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido no encontrado.",
        )

    if not _can_view_all_orders(db, current_user) and order.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los detalles de este pedido.",
        )

    try:
        return get_order_details_by_order_id(db, order_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/details/{detail_id}", response_model=OrderDetailRead)
def read_order_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    detail = get_order_detail_by_id(db, detail_id)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle de pedido no encontrado.",
        )

    if not _can_view_all_orders(db, current_user) and detail.pedido_rel.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este detalle de pedido.",
        )

    return detail


@router.post(
    "/details",
    response_model=OrderDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_order_detail(
    payload: OrderDetailCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    order = get_order_by_id(db, payload.pedido_id_pedido)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El pedido no existe.",
        )

    can_manage_all = user_has_any_permission(db, current_user, "gestionar_pedidos")

    if not can_manage_all and order.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para agregar detalles a este pedido.",
        )

    try:
        detail_obj = create_order_detail(db, payload)

        registrar_aplicacion(
            db,
            modulo="pedidos",
            evento="PEDIDO_ITEM_AGREGADO",
            descripcion=f"Producto {payload.producto_id_producto} x{payload.cantidad} agregado al pedido {payload.pedido_id_pedido}.",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="detalle_pedido",
            entidad_id=detail_obj.id_detallePed,
        )

        return detail_obj
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

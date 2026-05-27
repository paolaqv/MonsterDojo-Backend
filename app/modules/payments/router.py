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
from app.modules.payments.schemas import PaymentCreate, PaymentRead, PaymentUpdate
from app.modules.payments.service import (
    create_payment,
    get_payment_by_id,
    get_payments,
    update_payment,
)
from app.modules.users.model import Usuario


router = APIRouter(prefix="/payments", tags=["Payments"])


def _can_view_all_payments(db: Session, current_user: Usuario) -> bool:
    return user_has_any_permission(
        db,
        current_user,
        "ver_pagos",
        "gestionar_pagos",
    )


@router.get("/", response_model=list[PaymentRead])
def read_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    payments = get_payments(db, skip=skip, limit=limit)

    if _can_view_all_payments(db, current_user):
        return payments

    return [
        payment
        for payment in payments
        if payment.usuario_id_usuario == current_user.id_usuario
    ]


@router.get("/{payment_id}", response_model=PaymentRead)
def read_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    payment = get_payment_by_id(db, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado.",
        )

    if (
        not _can_view_all_payments(db, current_user)
        and payment.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este pago.",
        )

    return payment


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_new_payment(
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    can_manage_all = user_has_any_permission(db, current_user, "gestionar_pagos")

    if not can_manage_all and payload.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para registrar pagos para otro usuario.",
        )

    try:
        payment = create_payment(db, payload)

        registrar_aplicacion(
            db,
            modulo="pagos",
            evento="PAGO_PROCESADO",
            descripcion=f"Pago {payment.id_pago} procesado por usuario {current_user.id_usuario}, monto {payment.monto}.",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="pago",
            entidad_id=payment.id_pago,
        )

        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{payment_id}", response_model=PaymentRead)
def update_existing_payment(
    payment_id: int,
    payload: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_permissions("gestionar_pagos")),
):
    try:
        payment = update_payment(db, payment_id, payload)

        registrar_aplicacion(
            db,
            modulo="pagos",
            evento="PAGO_ACTUALIZADO",
            descripcion=f"Usuario {current_user.id_usuario} actualizo pago {payment_id} (monto {payment.monto}).",
            severidad="INFO",
            estado="OK",
            usuario_id=current_user.id_usuario,
            entidad_afectada="pago",
            entidad_id=payment_id,
        )

        return payment
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Pago no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )

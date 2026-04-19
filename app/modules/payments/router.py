from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.payments.schemas import PaymentCreate, PaymentRead, PaymentUpdate
from app.modules.payments.service import (
    create_payment,
    get_payment_by_id,
    get_payments,
    update_payment,
)


router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=list[PaymentRead])
def read_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_payments(db, skip=skip, limit=limit)


@router.get("/{payment_id}", response_model=PaymentRead)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = get_payment_by_id(db, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pago no encontrado.",
        )

    return payment


@router.post("/", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_new_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    try:
        return create_payment(db, payload)
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
):
    try:
        return update_payment(db, payment_id, payload)
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
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.reservations.schemas import (
    ReservationCreate,
    ReservationDetailCreate,
    ReservationDetailRead,
    ReservationRead,
    ReservationUpdate,
)
from app.modules.reservations.service import (
    create_reservation,
    create_reservation_detail,
    get_reservation_by_id,
    get_reservation_detail_by_id,
    get_reservation_details_by_reservation_id,
    get_reservations,
    update_reservation,
)


router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=list[ReservationRead])
def read_reservations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_reservations(db, skip=skip, limit=limit)


@router.get("/{reservation_id}", response_model=ReservationRead)
def read_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return reservation


@router.post("/", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_new_reservation(payload: ReservationCreate, db: Session = Depends(get_db)):
    try:
        return create_reservation(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{reservation_id}", response_model=ReservationRead)
def update_existing_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
    db: Session = Depends(get_db),
):
    try:
        return update_reservation(db, reservation_id, payload)
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Reserva no encontrada."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )


@router.get("/{reservation_id}/details", response_model=list[ReservationDetailRead])
def read_reservation_details(reservation_id: int, db: Session = Depends(get_db)):
    try:
        return get_reservation_details_by_reservation_id(db, reservation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/details/{detail_id}", response_model=ReservationDetailRead)
def read_reservation_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = get_reservation_detail_by_id(db, detail_id)

    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Detalle de reserva no encontrado.",
        )

    return detail


@router.post(
    "/details",
    response_model=ReservationDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_reservation_detail(
    payload: ReservationDetailCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_reservation_detail(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
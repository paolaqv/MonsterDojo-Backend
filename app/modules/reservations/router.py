# app/modules/reservations/router.py

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.auth.permissions import require_roles
from app.modules.reservations.schemas import (
    ReservationCheckoutRequest,
    ReservationCheckoutResponse,
    ReservationCreate,
    ReservationDetailCreate,
    ReservationDetailRead,
    ReservationRead,
    ReservationUpdate,
)
from app.modules.reservations.service import (
    create_reservation,
    create_reservation_checkout,
    create_reservation_detail,
    get_active_reservation_for_user,
    get_reservation_by_id,
    get_reservation_by_id_admin,
    get_reservation_detail_by_id,
    get_reservation_details_by_reservation_id,
    get_reservation_details_by_reservation_id_admin,
    get_reservations,
    update_reservation,
    update_reservation_checkout,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/active", response_model=ReservationRead)
def read_active_reservation(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_active_reservation_for_user(db, current_user.id_usuario)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tienes una reserva activa.",
        )

    return reservation


@router.get("/", response_model=list[ReservationRead])
def read_reservations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return get_reservations(
        db,
        skip=skip,
        limit=limit,
        user_id=current_user.id_usuario,
    )

@router.get("/admin", response_model=list[ReservationRead])
def read_reservations_admin(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoLocal")),
):
    return get_reservations(
        db,
        skip=skip,
        limit=limit,
        user_id=None,
    )

@router.get("/admin/{reservation_id}", response_model=ReservationRead)
def read_reservation_admin(
    reservation_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoLocal")),
):

    reservation = get_reservation_by_id_admin(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    return reservation


@router.get("/{reservation_id}", response_model=ReservationRead)
def read_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    if reservation.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta reserva.",
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


@router.get(
    "/admin/{reservation_id}/details",
    response_model=list[ReservationDetailRead],
)
def read_reservation_details_admin(
    reservation_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoLocal")),
):
    try:
        return get_reservation_details_by_reservation_id_admin(db, reservation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/{reservation_id}/details", response_model=list[ReservationDetailRead])
def read_reservation_details(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada.",
        )

    if reservation.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver los detalles de esta reserva.",
        )

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


@router.post("/checkout", response_model=ReservationCheckoutResponse)
def checkout_reservation(
    payload: ReservationCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        return create_reservation_checkout(
            db,
            payload=payload,
            current_user=current_user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar la reserva: {str(e)}",
        )


@router.put("/{reservation_id}/checkout", response_model=ReservationCheckoutResponse)
def update_checkout_reservation(
    reservation_id: int,
    payload: ReservationCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        return update_reservation_checkout(
            db,
            reservation_id=reservation_id,
            payload=payload,
            current_user=current_user,
        )
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la reserva: {str(e)}",
        )
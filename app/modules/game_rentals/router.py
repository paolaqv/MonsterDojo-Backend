from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.permissions import user_has_any_permission
from app.modules.game_rentals.schemas import (
    GameRentalCreate,
    GameRentalRead,
    GameRentalUpdate,
)
from app.modules.game_rentals.service import (
    create_game_rental,
    get_game_rental_by_id,
    get_game_rentals,
    get_game_rentals_by_reservation_id,
    update_game_rental,
)
from app.modules.reservations.service import get_reservation_by_id
from app.modules.users.model import Usuario

#mediacion completa: proteccion de peticiones en juegos
router = APIRouter(prefix="/game-rentals", tags=["Game Rentals"])


def _can_view_all_rentals(db: Session, current_user: Usuario) -> bool:
    return user_has_any_permission(
        db,
        current_user,
        "ver_reservas_detalle",
        "gestionar_reservas",
    )


def _can_manage_all_rentals(db: Session, current_user: Usuario) -> bool:
    return user_has_any_permission(
        db,
        current_user,
        "gestionar_reservas",
    )


@router.get("/", response_model=list[GameRentalRead])
def read_game_rentals(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    rentals = get_game_rentals(db, skip=skip, limit=limit)

    if _can_view_all_rentals(db, current_user):
        return rentals

    return [
        rental
        for rental in rentals
        if rental.usuario_id_usuario == current_user.id_usuario
    ]


@router.get("/{rental_id}", response_model=GameRentalRead)
def read_game_rental(
    rental_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    rental = get_game_rental_by_id(db, rental_id)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de juego no encontrado.",
        )

    if (
        not _can_view_all_rentals(db, current_user)
        and rental.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar este registro de juego.",
        )

    return rental


@router.get("/reservation/{reservation_id}", response_model=list[GameRentalRead])
def read_game_rentals_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_reservation_by_id(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva no existe.",
        )

    if (
        not _can_view_all_rentals(db, current_user)
        and reservation.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para consultar los juegos de esta reserva.",
        )

    return get_game_rentals_by_reservation_id(db, reservation_id)


@router.post("/", response_model=GameRentalRead, status_code=status.HTTP_201_CREATED)
def create_new_game_rental(
    payload: GameRentalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    reservation = get_reservation_by_id(db, payload.reserva_id_reserva)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La reserva no existe.",
        )

    can_manage_all = _can_manage_all_rentals(db, current_user)

    if (
        not can_manage_all
        and reservation.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para registrar juegos en esta reserva.",
        )

    if (
        not can_manage_all
        and payload.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes registrar juegos para otro usuario.",
        )

    try:
        return create_game_rental(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{rental_id}", response_model=GameRentalRead)
def update_existing_game_rental(
    rental_id: int,
    payload: GameRentalUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    rental = get_game_rental_by_id(db, rental_id)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de juego no encontrado.",
        )

    can_manage_all = _can_manage_all_rentals(db, current_user)

    if (
        not can_manage_all
        and rental.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este registro de juego.",
        )

    if (
        not can_manage_all
        and payload.usuario_id_usuario is not None
        and payload.usuario_id_usuario != current_user.id_usuario
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes reasignar el registro a otro usuario.",
        )

    if payload.reserva_id_reserva is not None:
        new_reservation = get_reservation_by_id(db, payload.reserva_id_reserva)

        if not new_reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="La reserva no existe.",
            )

        if (
            not can_manage_all
            and new_reservation.usuario_id_usuario != current_user.id_usuario
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes asociar el registro a una reserva ajena.",
            )

    try:
        return update_game_rental(db, rental_id, payload)
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Registro de juego no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )
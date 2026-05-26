from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
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


router = APIRouter(prefix="/game-rentals", tags=["Game Rentals"])


@router.get("/", response_model=list[GameRentalRead])
def read_game_rentals(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_game_rentals(db, skip=skip, limit=limit)


@router.get("/{rental_id}", response_model=GameRentalRead)
def read_game_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = get_game_rental_by_id(db, rental_id)

    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de juego no encontrado.",
        )

    return rental


@router.get("/reservation/{reservation_id}", response_model=list[GameRentalRead])
def read_game_rentals_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_game_rentals_by_reservation_id(db, reservation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/", response_model=GameRentalRead, status_code=status.HTTP_201_CREATED)
def create_new_game_rental(
    payload: GameRentalCreate,
    db: Session = Depends(get_db),
):
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
):
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
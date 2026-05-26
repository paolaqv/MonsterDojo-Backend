from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.activity.service import registrar_evento
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.permissions import (
    require_permissions,
    user_has_any_permission,
)
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
from app.modules.users.model import Usuario


router = APIRouter(prefix="/game-rentals", tags=["Game Rentals"])


def _can_view_all_rentals(db: Session, current_user: Usuario) -> bool:
    return user_has_any_permission(
        db,
        current_user,
        "ver_alquileres",
        "gestionar_alquileres",
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
            detail="No tienes permiso para ver este alquiler de juego.",
        )

    return rental


@router.get("/reservation/{reservation_id}", response_model=list[GameRentalRead])
def read_game_rentals_by_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        rentals = get_game_rentals_by_reservation_id(db, reservation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    if _can_view_all_rentals(db, current_user):
        return rentals

    return [
        rental
        for rental in rentals
        if rental.usuario_id_usuario == current_user.id_usuario
    ]


@router.post("/", response_model=GameRentalRead, status_code=status.HTTP_201_CREATED)
def create_new_game_rental(
    payload: GameRentalCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    can_manage_all = user_has_any_permission(db, current_user, "gestionar_alquileres")

    if not can_manage_all and payload.usuario_id_usuario != current_user.id_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para registrar alquileres para otro usuario.",
        )

    try:
        rental = create_game_rental(db, payload)

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ALQUILER_REGISTRADO",
            modulo="alquileres",
            accion="CREATE",
            estado="OK",
            severidad="MEDIA",
            entidad_afectada="registro_juego",
            entidad_id=rental.id_regJuego,
            valor_nuevo={
                "juego_id_juego": rental.juego_id_juego,
                "cantidad": rental.cantidad,
                "precio": rental.precio,
                "usuario_id_usuario": rental.usuario_id_usuario,
            },
        )

        return rental
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
    current_user: Usuario = Depends(require_permissions("gestionar_alquileres")),
):
    rental_before = get_game_rental_by_id(db, rental_id)
    snapshot_before = None
    if rental_before:
        snapshot_before = {
            "cantidad": rental_before.cantidad,
            "precio": rental_before.precio,
            "juego_id_juego": rental_before.juego_id_juego,
            "usuario_id_usuario": rental_before.usuario_id_usuario,
        }

    try:
        rental = update_game_rental(db, rental_id, payload)

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ALQUILER_ACTUALIZADO",
            modulo="alquileres",
            accion="UPDATE",
            estado="OK",
            severidad="MEDIA",
            entidad_afectada="registro_juego",
            entidad_id=rental_id,
            valor_anterior=snapshot_before,
            valor_nuevo={
                "cantidad": rental.cantidad,
                "precio": rental.precio,
                "juego_id_juego": rental.juego_id_juego,
                "usuario_id_usuario": rental.usuario_id_usuario,
            },
        )

        return rental
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

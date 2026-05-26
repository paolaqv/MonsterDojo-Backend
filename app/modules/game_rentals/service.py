from sqlalchemy.orm import Session

from app.modules.game_rentals import repository
from app.modules.game_rentals.model import RegistroJuego
from app.modules.game_rentals.schemas import GameRentalCreate, GameRentalUpdate


def get_game_rental_by_id(db: Session, rental_id: int) -> RegistroJuego | None:
    return repository.get_game_rental_by_id(db, rental_id)


def get_game_rentals(db: Session, skip: int = 0, limit: int = 100) -> list[RegistroJuego]:
    return repository.get_game_rentals(db, skip=skip, limit=limit)


def get_game_rentals_by_reservation_id(
    db: Session,
    reservation_id: int,
) -> list[RegistroJuego]:
    reservation = repository.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("La reserva no existe.")

    return repository.get_game_rentals_by_reservation_id(db, reservation_id)


def create_game_rental(db: Session, rental_data: GameRentalCreate) -> RegistroJuego:
    game = repository.get_game_by_id(db, rental_data.juego_id_juego)
    if not game:
        raise ValueError("El juego no existe.")

    user = repository.get_user_by_id(db, rental_data.usuario_id_usuario)
    if not user:
        raise ValueError("El usuario no existe.")

    reservation = repository.get_reservation_by_id(db, rental_data.reserva_id_reserva)
    if not reservation:
        raise ValueError("La reserva no existe.")

    return repository.create_game_rental(db, rental_data)


def update_game_rental(
    db: Session,
    rental_id: int,
    rental_data: GameRentalUpdate,
) -> RegistroJuego:
    rental = repository.get_game_rental_by_id(db, rental_id)
    if not rental:
        raise ValueError("Registro de juego no encontrado.")

    if rental_data.juego_id_juego is not None:
        game = repository.get_game_by_id(db, rental_data.juego_id_juego)
        if not game:
            raise ValueError("El juego no existe.")

    if rental_data.usuario_id_usuario is not None:
        user = repository.get_user_by_id(db, rental_data.usuario_id_usuario)
        if not user:
            raise ValueError("El usuario no existe.")

    if rental_data.reserva_id_reserva is not None:
        reservation = repository.get_reservation_by_id(db, rental_data.reserva_id_reserva)
        if not reservation:
            raise ValueError("La reserva no existe.")

    return repository.update_game_rental(db, rental, rental_data)
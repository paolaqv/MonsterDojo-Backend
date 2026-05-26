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

    if reservation.estado != "Reservado":
        raise ValueError("Solo se pueden agregar juegos a reservas activas.")

    if not game.activo:
        raise ValueError("El juego seleccionado no está disponible.")

    if reservation.usuario_id_usuario != rental_data.usuario_id_usuario:
        raise ValueError("El usuario indicado no corresponde a la reserva.")

    rental_data = rental_data.model_copy(
        update={"precio": game.precio_alquiler}
    )

    return repository.create_game_rental(db, rental_data)


def update_game_rental(
    db: Session,
    rental_id: int,
    rental_data: GameRentalUpdate,
) -> RegistroJuego:
    rental = repository.get_game_rental_by_id(db, rental_id)
    if not rental:
        raise ValueError("Registro de juego no encontrado.")

    game_id = (
        rental_data.juego_id_juego
        if rental_data.juego_id_juego is not None
        else rental.juego_id_juego
    )
    user_id = (
        rental_data.usuario_id_usuario
        if rental_data.usuario_id_usuario is not None
        else rental.usuario_id_usuario
    )
    reservation_id = (
        rental_data.reserva_id_reserva
        if rental_data.reserva_id_reserva is not None
        else rental.reserva_id_reserva
    )

    game = repository.get_game_by_id(db, game_id)
    if not game:
        raise ValueError("El juego no existe.")

    user = repository.get_user_by_id(db, user_id)
    if not user:
        raise ValueError("El usuario no existe.")

    reservation = repository.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise ValueError("La reserva no existe.")

    if reservation.estado != "Reservado":
        raise ValueError("Solo se pueden modificar juegos de reservas activas.")

    if not game.activo:
        raise ValueError("El juego seleccionado no está disponible.")

    if reservation.usuario_id_usuario != user_id:
        raise ValueError("El usuario indicado no corresponde a la reserva.")

    rental_data = rental_data.model_copy(
        update={
            "juego_id_juego": game_id,
            "usuario_id_usuario": user_id,
            "reserva_id_reserva": reservation_id,
            "precio": game.precio_alquiler,
        }
    )

    return repository.update_game_rental(db, rental, rental_data)
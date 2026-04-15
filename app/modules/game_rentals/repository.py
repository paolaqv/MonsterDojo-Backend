from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.game_rentals.model import RegistroJuego
from app.modules.game_rentals.schemas import GameRentalCreate, GameRentalUpdate
from app.modules.games.model import Juego
from app.modules.reservations.model import Reserva
from app.modules.users.model import Usuario


def get_game_by_id(db: Session, game_id: int) -> Juego | None:
    stmt = select(Juego).where(Juego.id_juego == game_id)
    return db.scalar(stmt)


def get_user_by_id(db: Session, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id_usuario == user_id)
    return db.scalar(stmt)


def get_reservation_by_id(db: Session, reservation_id: int) -> Reserva | None:
    stmt = select(Reserva).where(Reserva.id_reserva == reservation_id)
    return db.scalar(stmt)


def get_game_rental_by_id(db: Session, rental_id: int) -> RegistroJuego | None:
    stmt = select(RegistroJuego).where(RegistroJuego.id_regJuego == rental_id)
    return db.scalar(stmt)


def get_game_rentals(db: Session, skip: int = 0, limit: int = 100) -> list[RegistroJuego]:
    stmt = select(RegistroJuego).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_game_rentals_by_reservation_id(
    db: Session,
    reservation_id: int,
) -> list[RegistroJuego]:
    stmt = select(RegistroJuego).where(RegistroJuego.reserva_id_reserva == reservation_id)
    return list(db.scalars(stmt).all())


def create_game_rental(db: Session, rental_data: GameRentalCreate) -> RegistroJuego:
    rental = RegistroJuego(
        cantidad=rental_data.cantidad,
        precio=rental_data.precio,
        tipo=rental_data.tipo,
        juego_id_juego=rental_data.juego_id_juego,
        usuario_id_usuario=rental_data.usuario_id_usuario,
        reserva_id_reserva=rental_data.reserva_id_reserva,
    )

    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


def update_game_rental(
    db: Session,
    rental: RegistroJuego,
    rental_data: GameRentalUpdate,
) -> RegistroJuego:
    update_data = rental_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(rental, field, value)

    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental
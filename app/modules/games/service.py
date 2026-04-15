from sqlalchemy.orm import Session

from app.modules.games import repository
from app.modules.games.model import CategoriaJuego, Juego
from app.modules.games.schemas import GameCategoryCreate, GameCreate, GameUpdate


def get_game_category_by_id(db: Session, category_id: int) -> CategoriaJuego | None:
    return repository.get_game_category_by_id(db, category_id)


def get_game_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoriaJuego]:
    return repository.get_game_categories(db, skip=skip, limit=limit)


def create_game_category(db: Session, category_data: GameCategoryCreate) -> CategoriaJuego:
    return repository.create_game_category(db, category_data)


def get_game_by_id(db: Session, game_id: int) -> Juego | None:
    return repository.get_game_by_id(db, game_id)


def get_games(db: Session, skip: int = 0, limit: int = 100) -> list[Juego]:
    return repository.get_games(db, skip=skip, limit=limit)


def create_game(db: Session, game_data: GameCreate) -> Juego:
    category = repository.get_game_category_by_id(
        db, game_data.categoria_juego_id_catJuego
    )
    if not category:
        raise ValueError("La categoría del juego no existe.")

    return repository.create_game(db, game_data)


def update_game(db: Session, game_id: int, game_data: GameUpdate) -> Juego:
    game = repository.get_game_by_id(db, game_id)
    if not game:
        raise ValueError("Juego no encontrado.")

    if game_data.categoria_juego_id_catJuego is not None:
        category = repository.get_game_category_by_id(
            db, game_data.categoria_juego_id_catJuego
        )
        if not category:
            raise ValueError("La categoría del juego no existe.")

    return repository.update_game(db, game, game_data)
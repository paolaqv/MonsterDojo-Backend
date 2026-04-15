from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.games.model import CategoriaJuego, Juego
from app.modules.games.schemas import GameCategoryCreate, GameCreate, GameUpdate


def get_game_category_by_id(db: Session, category_id: int) -> CategoriaJuego | None:
    stmt = select(CategoriaJuego).where(CategoriaJuego.id_catJuego == category_id)
    return db.scalar(stmt)


def get_game_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoriaJuego]:
    stmt = select(CategoriaJuego).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_game_category(db: Session, category_data: GameCategoryCreate) -> CategoriaJuego:
    category = CategoriaJuego(nombre=category_data.nombre)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_game_by_id(db: Session, game_id: int) -> Juego | None:
    stmt = select(Juego).where(Juego.id_juego == game_id)
    return db.scalar(stmt)


def get_games(db: Session, skip: int = 0, limit: int = 100) -> list[Juego]:
    stmt = select(Juego).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_game(db: Session, game_data: GameCreate) -> Juego:
    game = Juego(
        nombre=game_data.nombre,
        descripcion=game_data.descripcion,
        precio_alquiler=game_data.precio_alquiler,
        precio_venta=game_data.precio_venta,
        disponible_venta=game_data.disponible_venta,
        imagen=game_data.imagen,
        activo=game_data.activo,
        categoria_juego_id_catJuego=game_data.categoria_juego_id_catJuego,
    )

    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def update_game(db: Session, game: Juego, game_data: GameUpdate) -> Juego:
    update_data = game_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(game, field, value)

    db.add(game)
    db.commit()
    db.refresh(game)
    return game
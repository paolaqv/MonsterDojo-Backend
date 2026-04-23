from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.permissions import require_permissions
from app.modules.games.schemas import (
    GameCategoryCreate,
    GameCategoryRead,
    GameCreate,
    GameRead,
    GameUpdate,
)
from app.modules.games.service import (
    create_game,
    create_game_category,
    get_game_by_id,
    get_game_categories,
    get_games,
    update_game,
)
from app.modules.users.model import Usuario

router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/categories", response_model=list[GameCategoryRead])
def read_game_categories(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_juegos")),
):
    return get_game_categories(db, skip=skip, limit=limit)


@router.post(
    "/categories",
    response_model=GameCategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_game_category(
    payload: GameCategoryCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_juegos")),
):
    return create_game_category(db, payload)


@router.get("/", response_model=list[GameRead])
def read_games(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_juegos")),
):
    return get_games(db, skip=skip, limit=limit)


@router.get("/{game_id}", response_model=GameRead)
def read_game(
    game_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_juegos")),
):
    game = get_game_by_id(db, game_id)

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Juego no encontrado.",
        )

    return game


@router.post("/", response_model=GameRead, status_code=status.HTTP_201_CREATED)
def create_new_game(
    payload: GameCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_juegos")),
):
    try:
        return create_game(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put("/{game_id}", response_model=GameRead)
def update_existing_game(
    game_id: int,
    payload: GameUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_juegos")),
):
    try:
        return update_game(db, game_id, payload)
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Juego no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )
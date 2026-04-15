from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.tables.router import router as tables_router
from app.modules.products.router import router as products_router
from app.modules.games.router import router as games_router


api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(tables_router)
api_router.include_router(products_router)
api_router.include_router(games_router)

@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Monster Dojo API is running"
    }
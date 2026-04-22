from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.tables.router import router as tables_router
from app.modules.products.router import router as products_router
from app.modules.games.router import router as games_router
from app.modules.reservations.router import router as reservations_router
from app.modules.orders.router import router as orders_router
from app.modules.game_rentals.router import router as game_rentals_router
from app.modules.payments.router import router as payments_router
from app.modules.users.security_router import router as security_users_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(tables_router)
api_router.include_router(products_router)
api_router.include_router(games_router)
api_router.include_router(reservations_router)
api_router.include_router(orders_router)
api_router.include_router(game_rentals_router)
api_router.include_router(payments_router)
api_router.include_router(security_users_router)

@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "message": "Monster Dojo API is running"
    }
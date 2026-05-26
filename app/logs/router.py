from fastapi import APIRouter

from app.logs.activity.router import router as activity_router
from app.logs.application.router import router as application_router

router = APIRouter()

router.include_router(activity_router)
router.include_router(application_router)

from fastapi import APIRouter
from app.logs.activity.router import router as activity_router

router=APIRouter()

router.include_router(
   activity_router
)
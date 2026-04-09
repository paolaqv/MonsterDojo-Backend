from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserRead


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: Usuario = Depends(get_current_user)):
    return current_user
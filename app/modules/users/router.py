from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserRead, UserUpdateSelf
from app.modules.users.service import update_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: Usuario = Depends(get_current_user),
):
    return current_user


@router.put("/me/profile", response_model=UserRead)
def update_me(
    payload: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    return update_current_user(db, current_user, payload)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserRead, UserUpdate
from app.modules.users.service import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
)

router = APIRouter(
    prefix="/security/users",
    tags=["Security Users"],
)


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return get_all_users(db)


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_security_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        return update_user(db, user_id, payload)
    except ValueError as e:
        detail = str(e)
        status_code = (
            status.HTTP_404_NOT_FOUND
            if detail == "Usuario no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
        )


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_security_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        delete_user(db, user_id)
        return {"message": "Usuario eliminado correctamente."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
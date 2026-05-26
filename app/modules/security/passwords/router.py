from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.permissions import require_roles
from app.modules.security.passwords.schemas import PasswordPolicyRead, PasswordPolicyUpdate
from app.modules.security.passwords.service import get_active_password_policy, update_password_policy
from app.modules.users.model import Usuario

router = APIRouter(
    prefix="/security/password-policy",
    tags=["Security Password Policy"],
)


@router.get("/", response_model=PasswordPolicyRead)
def read_password_policy(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return get_active_password_policy(db)


@router.put("/", response_model=PasswordPolicyRead)
def edit_password_policy(
    payload: PasswordPolicyUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        return update_password_policy(db, payload, current_user.id_usuario)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
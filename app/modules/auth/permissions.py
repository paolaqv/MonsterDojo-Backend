from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_permissions


def require_roles(*allowed_roles: str):
    def checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol_id_rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )
        return current_user

    return checker


def _user_permissions(db: Session, current_user: Usuario) -> set[str]:
    return set(get_user_permissions(db, current_user.id_usuario))


def require_permissions(*required_permissions: str):
    def checker(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        permissions = _user_permissions(db, current_user)

        missing = [perm for perm in required_permissions if perm not in permissions]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )

        return current_user

    return checker


def require_any_permission(*allowed_permissions: str):
    def checker(
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_user),
    ) -> Usuario:
        permissions = _user_permissions(db, current_user)

        if not any(perm in permissions for perm in allowed_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )

        return current_user

    return checker


def user_has_any_permission(
    db: Session,
    current_user: Usuario,
    *allowed_permissions: str,
) -> bool:
    permissions = _user_permissions(db, current_user)
    return any(perm in permissions for perm in allowed_permissions)
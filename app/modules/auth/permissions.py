from fastapi import Depends, HTTPException, status
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario


def require_roles(*allowed_roles: str):
    def checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        if current_user.rol_id_rol not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para acceder a este recurso",
            )
        return current_user

    return checker
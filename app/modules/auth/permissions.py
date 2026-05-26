from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_permissions


ROLE_ACCESS_MATRIX = {
    "cliente": {
        "reservas": ["crear", "ver_propias", "cancelar_propias"],
        "pedidos": ["crear", "ver_propios", "cancelar_propios"],
        "perfil": ["ver_propio", "editar_propio"],
    },
    "mesero": {
        "pedidos": ["ver", "gestionar_estado"],
        "reservas": ["ver"],
        "mesas": ["ver"],
    },
    "encargadoLocal": {
        "productos": ["ver", "gestionar"],
        "juegos": ["ver", "gestionar"],
        "mesas": ["ver", "gestionar"],
        "pedidos": ["ver", "gestionar"],
        "reservas": ["ver", "gestionar"],
    },
    "encargadoSeguridad": {
        "usuarios": ["ver", "gestionar_roles", "gestionar_estado"],
        "roles": ["ver", "gestionar"],
        "auditoria": ["ver", "filtrar", "monitorear_criticos"],
        "politicas_password": ["ver", "gestionar"],
    },
}

MODULE_ACTION_PERMISSIONS = {
    "products:read": "ver_productos",
    "products:manage": "gestionar_productos",
    "games:read": "ver_juegos",
    "games:manage": "gestionar_juegos",
    "tables:read": "ver_mesas",
    "tables:manage": "gestionar_mesas",
    "orders:read_detail": "ver_pedidos_detalle",
    "orders:manage": "gestionar_pedidos",
    "reservations:create": "crear_reservas",
    "reservations:read_detail": "ver_reservas_detalle",
    "reservations:manage": "gestionar_reservas",
    "users:read": "ver_usuarios",
}


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

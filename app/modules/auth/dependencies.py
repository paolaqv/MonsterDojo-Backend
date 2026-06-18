from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.modules.users.model import Usuario
from app.modules.users.service import get_user_by_id


settings = get_settings()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la credencial.",
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
        )
        subject: str | None = payload.get("sub")

        if subject is None:
            raise credentials_exception

        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active or not user.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario está inactivo.",
        )
#mediacion completa
    if user.bloqueado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="La cuenta del usuario se encuentra bloqueada.",
        )

    # Expiracion de acceso: se valida en CADA peticion (no solo al iniciar
    # sesion) para que una sesion ya iniciada quede bloqueada en cuanto venza
    # la fecha. La columna es TIMESTAMP (naive); se asume UTC para comparar.
    if user.acceso_expira and user.fecha_expiracion_acceso is not None:
        expira = user.fecha_expiracion_acceso
        if expira.tzinfo is None:
            expira = expira.replace(tzinfo=timezone.utc)

        if expira <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tu acceso al sistema ha expirado. Contacta al administrador.",
            )

    if user.rol is None or not user.rol.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El rol asignado al usuario se encuentra inactivo.",
        )

    return user

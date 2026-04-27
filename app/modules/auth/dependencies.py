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
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
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

    return user
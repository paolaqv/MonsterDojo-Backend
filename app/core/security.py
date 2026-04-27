from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

settings = get_settings()


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)

    expire = now + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.modules.users.schemas import CurrentUserWithPermissionsRead, UserRead
from app.shared.validation import (
    ensure_person_name,
    ensure_valid_phone,
    ROLE_ID_PATTERN,
)
#tolerancia de errores,entrada de datos

class LoginRequest(BaseModel):
    correo: EmailStr
    recaptcha_token: str
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: CurrentUserWithPermissionsRead


class RegisterRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr

    codigo_verificacion: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

    telefono: int | None = None
    password: str = Field(..., min_length=12, max_length=256)
    rol_id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)

    @field_validator("correo")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def validate_names(cls, value, info):
        return ensure_person_name(value, info.field_name)

    @field_validator("telefono", mode="before")
    @classmethod
    def validate_phone(cls, value):
        return ensure_valid_phone(value)

class EmailVerificationRequest(BaseModel):
    correo: EmailStr


class EmailVerificationConfirmRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class MessageResponse(BaseModel):
    message: str


# =========================================================
# LEGACY: recuperación por pregunta de seguridad
# =========================================================

class SecurityQuestionRequest(BaseModel):
    correo: EmailStr


class SecurityQuestionResponse(BaseModel):
    correo: EmailStr
    pregunta_seguridad: str


# =========================================================
# NUEVO: cambio obligatorio de contraseña
# =========================================================

class PasswordChangeRequiredRequest(BaseModel):
    correo: EmailStr
    current_password: str = Field(..., min_length=1, max_length=256)
    new_password: str = Field(..., min_length=1, max_length=256)


# =========================================================
# NUEVO: recuperación segura por código
# =========================================================

class PasswordRecoveryRequest(BaseModel):
    correo: EmailStr


class PasswordRecoveryVerifyRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class PasswordRecoveryResetRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=1, max_length=256)

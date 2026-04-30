from pydantic import BaseModel, EmailStr, Field, field_validator
from app.modules.users.schemas import CurrentUserWithPermissionsRead, UserRead


class LoginRequest(BaseModel):
    correo: EmailStr
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
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    password: str = Field(..., min_length=6, max_length=256)
    rol_id_rol: str = Field(..., min_length=1, max_length=50)

    @field_validator("correo")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

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

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
    def validate_gmail_domain(cls, value: str) -> str:
        if not value.lower().endswith("@gmail.com"):
            raise ValueError("El correo debe pertenecer al dominio @gmail.com.")
        return value.lower()


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


class VerifySecurityAnswerRequest(BaseModel):
    correo: EmailStr
    respuesta_seguridad: str = Field(..., min_length=1, max_length=255)

    @field_validator("respuesta_seguridad", mode="before")
    @classmethod
    def validate_security_answer(cls, value):
        return ensure_plain_text(value)


class ResetPasswordRequest(BaseModel):
    correo: EmailStr
    respuesta_seguridad: str = Field(..., min_length=1, max_length=255)
    new_password: str = Field(..., min_length=6, max_length=256)

    @field_validator("respuesta_seguridad", mode="before")
    @classmethod
    def validate_reset_answer(cls, value):
        return ensure_plain_text(value)


class ChangeSecurityQuestionRequest(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1, max_length=256)
    nueva_pregunta_seguridad: str = Field(..., min_length=1, max_length=255)
    nueva_respuesta_seguridad: str = Field(..., min_length=1, max_length=255)

    @field_validator("nueva_pregunta_seguridad", "nueva_respuesta_seguridad", mode="before")
    @classmethod
    def validate_new_security_fields(cls, value):
        return ensure_plain_text(value)


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

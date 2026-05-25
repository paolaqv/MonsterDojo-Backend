from pydantic import BaseModel, EmailStr, Field, field_validator
from app.modules.users.schemas import CurrentUserWithPermissionsRead, UserRead, sanitize_name, sanitize_email, sanitize_phone


class LoginRequest(BaseModel):
    correo: EmailStr
    recaptcha_token: str
    password: str = Field(..., min_length=1, max_length=256)
    @field_validator("correo", mode="before")
    @classmethod
    def clean_login_email(cls, value):
        return sanitize_email(value)


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

    @field_validator("correo", mode="before")
    @classmethod
    def normalize_email(cls, value) -> str | None:
        return sanitize_email(value)

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def clean_names(cls, value):
        return sanitize_name(value)

    @field_validator("telefono", mode="before")
    @classmethod
    def clean_phone(cls, value):
        return sanitize_phone(value)

class EmailVerificationRequest(BaseModel):
    correo: EmailStr
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)


class EmailVerificationConfirmRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)

class MessageResponse(BaseModel):
    message: str


# =========================================================
# LEGACY: recuperación por pregunta de seguridad
# =========================================================

class SecurityQuestionRequest(BaseModel):
    correo: EmailStr
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)


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
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)


# =========================================================
# NUEVO: recuperación segura por código
# =========================================================

class PasswordRecoveryRequest(BaseModel):
    correo: EmailStr
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)

class PasswordRecoveryVerifyRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)


class PasswordRecoveryResetRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=1, max_length=256)
    @field_validator("correo", mode="before")
    @classmethod
    def clean_email(cls, value):
        return sanitize_email(value)

from pydantic import BaseModel, EmailStr, Field

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
    correo: EmailStr
    telefono: int | None = None
    password: str = Field(..., min_length=6, max_length=256)
    pregunta_seguridad: str = Field(..., min_length=1, max_length=255)
    respuesta_seguridad: str = Field(..., min_length=1, max_length=255)
    rol_id_rol: str = Field(..., min_length=1, max_length=50)


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


class ResetPasswordRequest(BaseModel):
    correo: EmailStr
    respuesta_seguridad: str = Field(..., min_length=1, max_length=255)
    new_password: str = Field(..., min_length=6, max_length=256)


class ChangeSecurityQuestionRequest(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1, max_length=256)
    nueva_pregunta_seguridad: str = Field(..., min_length=1, max_length=255)
    nueva_respuesta_seguridad: str = Field(..., min_length=1, max_length=255)


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
    codigo: str = Field(..., min_length=6, max_length=6)


class PasswordRecoveryResetRequest(BaseModel):
    correo: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=1, max_length=256)
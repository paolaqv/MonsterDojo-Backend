from pydantic import BaseModel, EmailStr, Field
from app.modules.users.schemas import UserRead


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(..., min_length=1, max_length=256)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead

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
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr
    telefono: int | None = None
    rol_id_rol: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True
    activo: bool = True


class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr
    telefono: int | None = None
    password: str = Field(..., min_length=6, max_length=256)
    pregunta_seguridad: str = Field(..., min_length=1, max_length=255)
    respuesta_seguridad: str = Field(..., min_length=1, max_length=255)
    rol_id_rol: str = Field(..., min_length=1, max_length=50)


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = None
    pregunta_seguridad: str | None = Field(default=None, min_length=1, max_length=255)
    respuesta_seguridad: str | None = Field(default=None, min_length=1, max_length=255)
    rol_id_rol: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None
    activo: bool | None = None


class UserRead(UserBase):
    id_usuario: int

    model_config = ConfigDict(from_attributes=True)


class UserWithSecurityRead(UserRead):
    pregunta_seguridad: str

    model_config = ConfigDict(from_attributes=True)
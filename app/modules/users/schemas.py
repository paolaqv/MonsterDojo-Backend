from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr
    telefono: int | None = None
    rol_id_rol: str = Field(..., min_length=1, max_length=50)
    is_active: bool = True
    activo: bool = True

class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = None
    password: str = Field(..., min_length=6, max_length=256)
    rol_id_rol: str = Field(..., min_length=1, max_length=50)
    enviar_credenciales: bool | None = False

    @field_validator("correo")
    @classmethod
    def validate_gmail_domain(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.lower().endswith("@gmail.com"):
            raise ValueError("El correo debe pertenecer al dominio @gmail.com.")
        return value.lower()


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = None
    rol_id_rol: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None
    activo: bool | None = None

    @field_validator("correo")
    @classmethod
    def validate_gmail_domain(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.lower().endswith("@gmail.com"):
            raise ValueError("El correo debe pertenecer al dominio @gmail.com.")
        return value.lower()


class UserRead(UserBase):
    id_usuario: int
    intentos_fallidos: int | None = 0
    bloqueado: bool | None = False
    requiere_cambio_password: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSelf(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr
    telefono: int | None = None


class UserRoleUpdate(BaseModel):
    rol_id_rol: str = Field(..., min_length=1, max_length=50)


class UserStatusUpdate(BaseModel):
    activo: bool


class CurrentUserWithPermissionsRead(UserRead):
    permisos: list[str] = []
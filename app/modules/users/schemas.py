from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.shared.validation import ROLE_ID_PATTERN, ensure_plain_text

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    rol_id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)
    is_active: bool = True
    activo: bool = True

    @field_validator("nombre", "rol_id_rol", mode="before")
    @classmethod
    def validate_user_base_text(cls, value):
        return ensure_plain_text(value)


class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    password: str = Field(..., min_length=6, max_length=256)
    pregunta_seguridad: str | None = None
    respuesta_seguridad: str | None = None
    rol_id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)

    @field_validator(
        "nombre",
        "pregunta_seguridad",
        "respuesta_seguridad",
        "rol_id_rol",
        mode="before",
    )
    @classmethod
    def validate_user_create_text(cls, value):
        return ensure_plain_text(value)


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    pregunta_seguridad: str | None = Field(default=None, min_length=1, max_length=255)
    respuesta_seguridad: str | None = Field(default=None, min_length=1, max_length=255)
    rol_id_rol: str | None = Field(default=None, min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)
    is_active: bool | None = None
    activo: bool | None = None

    @field_validator(
        "nombre",
        "pregunta_seguridad",
        "respuesta_seguridad",
        "rol_id_rol",
        mode="before",
    )
    @classmethod
    def validate_user_update_text(cls, value):
        return ensure_plain_text(value)


class UserRead(UserBase):
    id_usuario: int
    intentos_fallidos: int | None = 0
    bloqueado: bool | None = False
    requiere_cambio_password: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class UserWithSecurityRead(UserRead):
    pregunta_seguridad: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSelf(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    correo: EmailStr
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)

    @field_validator("nombre", mode="before")
    @classmethod
    def validate_self_text(cls, value):
        return ensure_plain_text(value, "nombre")


class UserRoleUpdate(BaseModel):
    rol_id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)

    @field_validator("rol_id_rol", mode="before")
    @classmethod
    def validate_role_text(cls, value):
        return ensure_plain_text(value, "rol_id_rol")


class UserStatusUpdate(BaseModel):
    activo: bool


class CurrentUserWithPermissionsRead(UserRead):
    permisos: list[str] = Field(default_factory=list)

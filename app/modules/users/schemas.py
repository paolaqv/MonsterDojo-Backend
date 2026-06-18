from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.shared.validation import (
    ensure_person_name,
    ensure_valid_phone,
    ensure_plain_text,
    ROLE_ID_PATTERN,
)

class UserBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr
    correo_contacto: EmailStr | None = None
    correo_contacto_verificado: bool = False
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    rol_id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)
    is_active: bool = True
    activo: bool = True
    acceso_expira: bool = False
    fecha_expiracion_acceso: datetime | None = None

class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)

    # Para cliente: correo real/login.
    # Para personal: correo real/contacto validado; el login se genera en backend.
    correo: EmailStr | None = None
    correo_contacto: EmailStr | None = None
    codigo_verificacion: str | None = Field(
        default=None,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
    )

    telefono: int | None = Field(default=None, ge=0, le=999999999999999)

    # Para cliente se usa el password que ingresa.
    # Para personal se genera temporal si no llega password.
    password: str | None = Field(default=None, min_length=8, max_length=256)

    # Rol opcional al crear el usuario: si no se asigna, el backend usa un rol
    # minimo por defecto. La asignacion del rol real puede hacerse despues.
    rol_id_rol: str | None = Field(default=None, max_length=50, pattern=ROLE_ID_PATTERN)
    enviar_credenciales: bool | None = False

    # Expiracion de acceso: si acceso_expira es True, fecha_expiracion_acceso es obligatoria.
    acceso_expira: bool | None = False
    fecha_expiracion_acceso: datetime | None = None

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def validate_names(cls, value, info):
        return ensure_person_name(value, info.field_name)

    @field_validator("telefono", mode="before")
    @classmethod
    def validate_phone(cls, value):
        return ensure_valid_phone(value)

class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    rol_id_rol: str | None = Field(default=None, min_length=3, max_length=50,  pattern=ROLE_ID_PATTERN)
    is_active: bool | None = None
    activo: bool | None = None
    acceso_expira: bool | None = None
    fecha_expiracion_acceso: datetime | None = None
    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def validate_names(cls, value, info):
        return ensure_person_name(value, info.field_name)

    @field_validator("telefono", mode="before")
    @classmethod
    def validate_phone(cls, value):
        return ensure_valid_phone(value)


class UserRead(UserBase):
    id_usuario: int
    intentos_fallidos: int | None = 0
    bloqueado: bool | None = False
    requiere_cambio_password: bool | None = False

    model_config = ConfigDict(from_attributes=True)


class UserUpdateSelf(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = None

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def validate_names(cls, value, info):
        return ensure_person_name(value, info.field_name)

    @field_validator("telefono", mode="before")
    @classmethod
    def validate_phone(cls, value):
        return ensure_valid_phone(value)


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

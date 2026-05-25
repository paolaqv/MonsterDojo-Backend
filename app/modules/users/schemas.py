from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


from app.shared.validation import ensure_plain_text, ROLE_ID_PATTERN
def sanitize_name(v: str | None) -> str | None:
    if isinstance(v, str):
        return " ".join(v.strip().split()).title()
    return v

def sanitize_email(v: str | None) -> str | None:
    if isinstance(v, str):
        return v.strip().lower()
    return v

def sanitize_phone(v) -> int | None:
    if isinstance(v, str):
        cleaned = "".join(c for c in v if c.isdigit())
        return int(cleaned) if cleaned else None
    return v

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

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def clean_names_base(cls, value):
        return sanitize_name(value)

    @field_validator("correo", "correo_contacto", mode="before")
    @classmethod
    def clean_emails_base(cls, value):
        return sanitize_email(value)

class UserCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    primer_apellido: str = Field(..., min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)

    # Para cliente: correo real/login.
    # Para personal: correo real/contacto validado; el login se genera en backend.
    correo: EmailStr | None = None
    correo_contacto: EmailStr | None = None
    codigo_verificacion: str | None = Field(default=None, min_length=6, max_length=6)

    telefono: int | None = None

    # Para cliente se usa el password que ingresa.
    # Para personal se genera temporal si no llega password.
    password: str | None = Field(default=None, min_length=8, max_length=256)

    rol_id_rol: str = Field(..., min_length=1, max_length=50)
    enviar_credenciales: bool | None = False

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def clean_names_create(cls, value):
        return sanitize_name(value)

    @field_validator("correo", "correo_contacto", mode="before")
    @classmethod
    def clean_emails_create(cls, value):
        return sanitize_email(value)

    @field_validator("telefono", mode="before")
    @classmethod
    def clean_phone_create(cls, value):
        return sanitize_phone(value)


class UserUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    primer_apellido: str | None = Field(default=None, min_length=1, max_length=50)
    segundo_apellido: str | None = Field(default=None, max_length=50)
    correo: EmailStr | None = None
    telefono: int | None = None
    rol_id_rol: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None
    activo: bool | None = None

    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def clean_names_update(cls, value):
        return sanitize_name(value)

    @field_validator("correo", mode="before")
    @classmethod
    def clean_email_update(cls, value):
        return sanitize_email(value)

    @field_validator("telefono", mode="before")
    @classmethod
    def clean_phone_update(cls, value):
        return sanitize_phone(value)


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
    telefono: int | None = Field(default=None, ge=0, le=999999999999999)
    
    @field_validator("nombre", "primer_apellido", "segundo_apellido", mode="before")
    @classmethod
    def validate_self_text(cls, value):
        cleaned = sanitize_name(value)
        if cleaned:
            return ensure_plain_text(cleaned, "nombre")
        return cleaned

    @field_validator("correo", mode="before")
    @classmethod
    def clean_email_self(cls, value):
        return sanitize_email(value)

    @field_validator("telefono", mode="before")
    @classmethod
    def clean_phone_self(cls, value):
        return sanitize_phone(value)


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

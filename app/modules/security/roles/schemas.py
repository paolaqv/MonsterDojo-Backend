from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import (
    PERMISSION_ID_PATTERN,
    ROLE_ID_PATTERN,
    ensure_plain_text,
    ensure_string_list,
)


class PermissionRead(BaseModel):
    id_permiso: str = Field(..., min_length=3, max_length=60, pattern=PERMISSION_ID_PATTERN)
    nombre: str = Field(..., min_length=1, max_length=120)
    modulo: str = Field(..., min_length=1, max_length=50)
    descripcion: Optional[str] = None
    activo: bool

    model_config = ConfigDict(from_attributes=True)


class RolePermissionUpdate(BaseModel):
    permisos: List[str] = Field(default_factory=list, max_length=200)

    @field_validator("permisos", mode="before")
    @classmethod
    def validate_permissions(cls, value):
        return ensure_string_list(value, "permisos", PERMISSION_ID_PATTERN)


class RoleRead(BaseModel):
    id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)
    nombre: str = Field(..., min_length=1, max_length=50)
    activo: bool = True
    permisos: List[str] = Field(default_factory=list)


class RoleCreate(BaseModel):
    id_rol: str = Field(..., min_length=3, max_length=50, pattern=ROLE_ID_PATTERN)
    nombre: str = Field(..., min_length=1, max_length=50)
    activo: bool = True
    permisos: List[str] = Field(default_factory=list, max_length=200)

    @field_validator("id_rol", "nombre", mode="before")
    @classmethod
    def validate_role_text(cls, value):
        return ensure_plain_text(value)

    @field_validator("permisos", mode="before")
    @classmethod
    def validate_role_permissions(cls, value):
        return ensure_string_list(value, "permisos", PERMISSION_ID_PATTERN)


class RoleUpdate(BaseModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=50)
    activo: Optional[bool] = None
    permisos: Optional[List[str]] = Field(default=None, max_length=200)

    @field_validator("nombre", mode="before")
    @classmethod
    def validate_role_update_text(cls, value):
        return ensure_plain_text(value)

    @field_validator("permisos", mode="before")
    @classmethod
    def validate_role_update_permissions(cls, value):
        return ensure_string_list(value, "permisos", PERMISSION_ID_PATTERN)


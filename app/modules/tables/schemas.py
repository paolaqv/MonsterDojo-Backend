from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text


class TableBase(BaseModel):
    capacidad: int = Field(..., ge=1, le=100)
    ubicacion: str = Field(..., min_length=1, max_length=200)
    activo: bool = True

    @field_validator("ubicacion", mode="before")
    @classmethod
    def validate_location(cls, value):
        return ensure_plain_text(value, "ubicacion")


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    capacidad: int | None = Field(default=None, ge=1, le=100)
    ubicacion: str | None = Field(default=None, min_length=1, max_length=200)
    activo: bool | None = None

    @field_validator("ubicacion", mode="before")
    @classmethod
    def validate_update_location(cls, value):
        return ensure_plain_text(value, "ubicacion")


class TableRead(TableBase):
    id_mesa: int

    model_config = ConfigDict(from_attributes=True)

class AvailableTableInfo(BaseModel):
    id_mesa: int
    capacidad: int
    ubicacion: str


class AvailableTableResponse(BaseModel):
    mesa: AvailableTableInfo
    disponible: bool
    proxima_disponibilidad: datetime | None = None

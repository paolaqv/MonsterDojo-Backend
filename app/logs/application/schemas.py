from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text


class ApplicationLogOut(BaseModel):
    id: int
    fecha: datetime

    modulo: str
    evento: str
    descripcion: Optional[str] = None

    severidad: Optional[str] = None
    estado: Optional[str] = None

    usuario_id: Optional[int] = None
    entidad_afectada: Optional[str] = None
    entidad_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationLogCreate(BaseModel):
    modulo: str = Field(..., min_length=1, max_length=100)
    evento: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = Field(default=None, max_length=2000)

    severidad: Optional[str] = Field(default="INFO", max_length=20)
    estado: Optional[str] = Field(default="OK", max_length=20)

    usuario_id: Optional[int] = Field(default=None, ge=1)
    entidad_afectada: Optional[str] = Field(default=None, max_length=100)
    entidad_id: Optional[str] = Field(default=None, max_length=50)

    @field_validator(
        "modulo",
        "evento",
        "descripcion",
        "severidad",
        "estado",
        "entidad_afectada",
        "entidad_id",
        mode="before",
    )
    @classmethod
    def validate_text(cls, value):
        return ensure_plain_text(value)

from datetime import datetime
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text


class ActivityLogCreate(BaseModel):

    usuario_id: Optional[int] = Field(default=None, ge=1)
    rol_id: Optional[str] = Field(default=None, min_length=3, max_length=50)

    evento: str = Field(..., min_length=1, max_length=80)
    modulo: str = Field(..., min_length=1, max_length=50)

    accion: Optional[str] = Field(default=None, max_length=30)
    descripcion: Optional[str] = Field(default=None, max_length=1000)

    ip_origen: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

    estado: Optional[str] = Field(default=None, max_length=20)
    severidad: Optional[Literal["BAJA", "MEDIA", "ALTA", "CRITICA"]] = None

    entidad_afectada: Optional[str] = Field(default=None, max_length=50)
    entidad_id: Optional[int] = Field(default=None, ge=1)

    valor_anterior: Optional[Dict[str, Any]] = None
    valor_nuevo: Optional[Dict[str, Any]] = None

    @field_validator(
        "rol_id",
        "evento",
        "modulo",
        "accion",
        "descripcion",
        "ip_origen",
        "user_agent",
        "estado",
        "entidad_afectada",
        mode="before",
    )
    @classmethod
    def validate_text_fields(cls, value):
        return ensure_plain_text(value)


class ActivityLogOut(ActivityLogCreate):
    id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)

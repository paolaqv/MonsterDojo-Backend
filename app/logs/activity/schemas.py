from datetime import datetime
import json
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text


class ActivityLogCreate(BaseModel):
    usuario_id: Optional[int] = Field(default=None, ge=1)
    rol_id: Optional[str] = Field(default=None, max_length=50)

    evento: str = Field(..., min_length=1, max_length=80)
    modulo: str = Field(..., min_length=1, max_length=50)

    accion: Optional[str] = Field(default=None, max_length=30)
    descripcion: Optional[str] = Field(default=None, max_length=1000)

    ip_origen: Optional[str] = Field(default=None, max_length=45)
    user_agent: Optional[str] = Field(default=None, max_length=500)

    estado: Optional[str] = Field(default=None, max_length=20)
    severidad: Optional[str] = Field(default=None, max_length=20)

    entidad_afectada: Optional[str] = Field(default=None, max_length=50)
    entidad_id: Optional[int] = Field(default=None)

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
        "severidad",
        "entidad_afectada",
        mode="before",
    )
    @classmethod
    def validate_text_fields(cls, value):
        return ensure_plain_text(value)

    @field_validator("valor_anterior", "valor_nuevo", mode="before")
    @classmethod
    def parse_json_values(cls, value):
        if value is None:
            return None

        if isinstance(value, dict):
            return value

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
                return {"value": parsed}
            except json.JSONDecodeError:
                return {"value": value}

        return {"value": value}


class ActivityLogOut(ActivityLogCreate):
    id: int
    fecha: datetime

    model_config = ConfigDict(from_attributes=True)
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.shared.validation import ensure_plain_text

# --- ACTIVOS ---
class ActivoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100)
    descripcion: str | None = Field(default=None, max_length=300)
    categoria: str = Field(..., min_length=1, max_length=50)

    @field_validator("nombre", "descripcion", "categoria", mode="before")
    @classmethod
    def validate_text(cls, value):
        if value:
            return ensure_plain_text(value)
        return value

class ActivoCreate(ActivoBase):
    pass

class ActivoUpdate(ActivoBase):
    nombre: str | None = Field(default=None, min_length=3, max_length=100)
    categoria: str | None = Field(default=None, min_length=1, max_length=50)

class ActivoRead(ActivoBase):
    id_activo: int
    model_config = ConfigDict(from_attributes=True)

# --- RIESGOS ---
class RiesgoBase(BaseModel):
    activo_id_activo: int = Field(..., ge=1)
    amenaza: str = Field(..., min_length=5, max_length=255)
    consecuencia: str = Field(..., min_length=10)
    probabilidad: int = Field(..., ge=1, le=5)
    impacto: int = Field(..., ge=1, le=5)
    riesgo_inherente: int
    nivel_inherente: str = Field(..., max_length=50)
    tratamiento: str = Field(..., max_length=50)

    @field_validator("amenaza", "consecuencia", "tratamiento", mode="before")
    @classmethod
    def validate_risk_text(cls, value):
        return ensure_plain_text(value)

class RiesgoCreate(RiesgoBase):
    pass

class RiesgoUpdate(BaseModel):
    activo_id_activo: int | None = Field(default=None, ge=1)
    amenaza: str | None = Field(default=None, min_length=5, max_length=255)
    consecuencia: str | None = Field(default=None, min_length=10)
    probabilidad: int | None = Field(default=None, ge=1, le=5)
    impacto: int | None = Field(default=None, ge=1, le=5)
    riesgo_inherente: int | None = None
    nivel_inherente: str | None = Field(default=None, max_length=50)
    tratamiento: str | None = Field(default=None, max_length=50)

class RiesgoRead(RiesgoBase):
    id_riesgo: int
    fecha_registro: datetime
    activo_nombre: str | None = None
    model_config = ConfigDict(from_attributes=True)

# --- MITIGACIONES ---
class MitigacionBase(BaseModel):
    riesgo_id_riesgo: int = Field(..., ge=1)
    control_implementado: str = Field(..., min_length=10)
    tipo: str = Field(..., max_length=2)
    nivel: str = Field(..., max_length=2)
    frecuencia: str | None = Field(default=None, max_length=50)
    probabilidad_residual: int = Field(..., ge=1, le=5)
    impacto_residual: int = Field(..., ge=1, le=5)
    riesgo_residual: int
    nivel_residual: str = Field(..., max_length=50)

    @field_validator("control_implementado", mode="before")
    @classmethod
    def validate_mitigation_text(cls, value):
        return ensure_plain_text(value)

class MitigacionCreate(MitigacionBase):
    pass

class MitigacionUpdate(BaseModel):
    control_implementado: str | None = Field(default=None, min_length=10)
    tipo: str | None = Field(default=None, max_length=2)
    nivel: str | None = Field(default=None, max_length=2)
    frecuencia: str | None = Field(default=None, max_length=50)
    probabilidad_residual: int | None = Field(default=None, ge=1, le=5)
    impacto_residual: int | None = Field(default=None, ge=1, le=5)
    riesgo_residual: int | None = None
    nivel_residual: str | None = Field(default=None, max_length=50)

class MitigacionRead(MitigacionBase):
    id_mitigacion: int
    model_config = ConfigDict(from_attributes=True)
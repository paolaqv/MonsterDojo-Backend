from pydantic import BaseModel, ConfigDict, Field


class PasswordPolicyRead(BaseModel):
    id: int
    longitud_minima: int
    dias_expiracion: int
    periodo_no_reutilizacion_meses: int
    requiere_mayusculas: bool
    requiere_minusculas: bool
    requiere_numeros: bool
    requiere_simbolos: bool
    max_intentos_login: int
    activa: bool

    model_config = ConfigDict(from_attributes=True)


class PasswordPolicyUpdate(BaseModel):
    longitud_minima: int = Field(..., ge=8, le=72)
    dias_expiracion: int = Field(..., ge=1, le=365)
    periodo_no_reutilizacion_meses: int = Field(..., ge=1, le=24)
    requiere_mayusculas: bool
    requiere_minusculas: bool
    requiere_numeros: bool
    requiere_simbolos: bool
    max_intentos_login: int = Field(..., ge=3, le=10)


class UnlockUserResponse(BaseModel):
    message: str
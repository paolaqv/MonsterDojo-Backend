from pydantic import BaseModel, ConfigDict, Field


class TableBase(BaseModel):
    capacidad: int = Field(..., ge=1)
    ubicacion: str = Field(..., min_length=1, max_length=200)
    activo: bool = True


class TableCreate(TableBase):
    pass


class TableUpdate(BaseModel):
    capacidad: int | None = Field(default=None, ge=1)
    ubicacion: str | None = Field(default=None, min_length=1, max_length=200)
    activo: bool | None = None


class TableRead(TableBase):
    id_mesa: int

    model_config = ConfigDict(from_attributes=True)
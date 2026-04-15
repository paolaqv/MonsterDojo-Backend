from pydantic import BaseModel, ConfigDict, Field


class GameCategoryBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)


class GameCategoryCreate(GameCategoryBase):
    pass


class GameCategoryRead(GameCategoryBase):
    id_catJuego: int

    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=500)
    precio_alquiler: float = Field(..., ge=0)
    precio_venta: float = Field(..., ge=0)
    disponible_venta: bool
    imagen: str = Field(..., min_length=1, max_length=255)
    activo: bool = True
    categoria_juego_id_catJuego: int


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    descripcion: str | None = Field(default=None, min_length=1, max_length=500)
    precio_alquiler: float | None = Field(default=None, ge=0)
    precio_venta: float | None = Field(default=None, ge=0)
    disponible_venta: bool | None = None
    imagen: str | None = Field(default=None, min_length=1, max_length=255)
    activo: bool | None = None
    categoria_juego_id_catJuego: int | None = None


class GameRead(GameBase):
    id_juego: int

    model_config = ConfigDict(from_attributes=True)
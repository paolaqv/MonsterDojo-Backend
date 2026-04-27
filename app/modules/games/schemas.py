from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text


class GameCategoryBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)

    @field_validator("nombre", mode="before")
    @classmethod
    def validate_category_text(cls, value):
        return ensure_plain_text(value, "nombre")


class GameCategoryCreate(GameCategoryBase):
    pass


class GameCategoryRead(GameCategoryBase):
    id_catJuego: int

    model_config = ConfigDict(from_attributes=True)


class GameBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: str = Field(..., min_length=1, max_length=500)
    precio_alquiler: float = Field(..., ge=0, le=100000)
    precio_venta: float = Field(..., ge=0, le=100000)
    disponible_venta: bool
    imagen: str = Field(..., min_length=1, max_length=255)
    activo: bool = True
    categoria_juego_id_catJuego: int = Field(..., ge=1)

    @field_validator("nombre", "descripcion", "imagen", mode="before")
    @classmethod
    def validate_game_text(cls, value):
        return ensure_plain_text(value)


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=50)
    descripcion: str | None = Field(default=None, min_length=1, max_length=500)
    precio_alquiler: float | None = Field(default=None, ge=0, le=100000)
    precio_venta: float | None = Field(default=None, ge=0, le=100000)
    disponible_venta: bool | None = None
    imagen: str | None = Field(default=None, min_length=1, max_length=255)
    activo: bool | None = None
    categoria_juego_id_catJuego: int | None = Field(default=None, ge=1)

    @field_validator("nombre", "descripcion", "imagen", mode="before")
    @classmethod
    def validate_game_update_text(cls, value):
        return ensure_plain_text(value)


class GameRead(GameBase):
    id_juego: int

    model_config = ConfigDict(from_attributes=True)

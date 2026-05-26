from pydantic import BaseModel, ConfigDict, Field

#tolerancia de errores,entrada de datos

class GameRentalBase(BaseModel):
    cantidad: int = Field(..., ge=1)
    precio: float = Field(..., ge=0)
    tipo: int = Field(..., ge=1)
    juego_id_juego: int = Field(..., ge=1)
    usuario_id_usuario: int = Field(..., ge=1)
    reserva_id_reserva: int = Field(..., ge=1)


class GameRentalCreate(GameRentalBase):
    pass


class GameRentalUpdate(BaseModel):
    cantidad: int | None = Field(default=None, ge=1)
    precio: float | None = Field(default=None, ge=0)
    tipo: int | None = None
    juego_id_juego: int | None = None
    usuario_id_usuario: int | None = None
    reserva_id_reserva: int | None = None


class GameRentalRead(GameRentalBase):
    id_regJuego: int

    model_config = ConfigDict(from_attributes=True)
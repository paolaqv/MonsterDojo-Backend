from pydantic import BaseModel, ConfigDict, Field


class GameRentalBase(BaseModel):
    cantidad: int = Field(..., ge=1)
    precio: float = Field(..., ge=0)
    tipo: int
    juego_id_juego: int
    usuario_id_usuario: int
    reserva_id_reserva: int


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
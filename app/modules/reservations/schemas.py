from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReservationBase(BaseModel):
    fecha_hora: datetime
    estado: str = Field(..., min_length=1, max_length=50)
    usuario_id_usuario: int
    mesa_id_mesa: int


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    fecha_hora: datetime | None = None
    estado: str | None = Field(default=None, min_length=1, max_length=50)
    usuario_id_usuario: int | None = None
    mesa_id_mesa: int | None = None


class ReservationRead(ReservationBase):
    id_reserva: int

    model_config = ConfigDict(from_attributes=True)


class ReservationDetailBase(BaseModel):
    cantidad: int = Field(..., ge=1)
    precio: float = Field(..., ge=0)
    producto_id_producto: int
    reserva_id_reserva: int


class ReservationDetailCreate(ReservationDetailBase):
    pass


class ReservationDetailRead(ReservationDetailBase):
    id_detalleReserva: int

    model_config = ConfigDict(from_attributes=True)

class ReservationCheckoutProductItem(BaseModel):
    id_producto: int
    cantidad: int = Field(..., gt=0)


class ReservationCheckoutRequest(BaseModel):
    date: str
    start_time: str
    end_time: str
    mesa_id: int
    productos: list[ReservationCheckoutProductItem] = []
    juego_id: int | None = None


class ReservationCheckoutResponse(BaseModel):
    message: str
    id_reserva: int
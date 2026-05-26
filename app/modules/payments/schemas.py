from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PaymentBase(BaseModel):
    fecha: datetime
    monto: float = Field(..., ge=0)
    detalle_pedido_id_detallePed: int
    detalle_reserva_id_detalleReserva: int
    registro_juego_id_regJuego: int
    usuario_id_usuario: int


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    fecha: datetime | None = None
    monto: float | None = Field(default=None, ge=0)
    detalle_pedido_id_detallePed: int | None = None
    detalle_reserva_id_detalleReserva: int | None = None
    registro_juego_id_regJuego: int | None = None
    usuario_id_usuario: int | None = None


class PaymentRead(PaymentBase):
    id_pago: int

    model_config = ConfigDict(from_attributes=True)
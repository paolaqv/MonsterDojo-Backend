from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


_PAYMENT_TARGET_FIELDS = (
    "detalle_pedido_id_detallePed",
    "detalle_reserva_id_detalleReserva",
    "registro_juego_id_regJuego",
)


class PaymentBase(BaseModel):
    fecha: datetime
    monto: float = Field(..., ge=0, le=1_000_000)
    detalle_pedido_id_detallePed: int | None = Field(default=None, ge=1)
    detalle_reserva_id_detalleReserva: int | None = Field(default=None, ge=1)
    registro_juego_id_regJuego: int | None = Field(default=None, ge=1)
    usuario_id_usuario: int = Field(..., ge=1)

    @model_validator(mode="after")
    def validate_single_target(self):
        provided = [
            field for field in _PAYMENT_TARGET_FIELDS if getattr(self, field) is not None
        ]
        if len(provided) != 1:
            raise ValueError(
                "Un pago debe asociarse a exactamente uno: detalle de pedido, detalle de reserva o registro de juego."
            )
        return self


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    fecha: datetime | None = None
    monto: float | None = Field(default=None, ge=0, le=1_000_000)
    detalle_pedido_id_detallePed: int | None = Field(default=None, ge=1)
    detalle_reserva_id_detalleReserva: int | None = Field(default=None, ge=1)
    registro_juego_id_regJuego: int | None = Field(default=None, ge=1)
    usuario_id_usuario: int | None = Field(default=None, ge=1)


class PaymentRead(BaseModel):
    id_pago: int
    fecha: datetime
    monto: float
    detalle_pedido_id_detallePed: int | None = None
    detalle_reserva_id_detalleReserva: int | None = None
    registro_juego_id_regJuego: int | None = None
    usuario_id_usuario: int

    model_config = ConfigDict(from_attributes=True)
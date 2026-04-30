from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.shared.validation import DATE_PATTERN, TIME_PATTERN, ensure_plain_text

ReservationState = Literal["Reservado", "Cancelado", "Finalizado"]


class ReservationBase(BaseModel):
    fecha_hora: datetime
    estado: ReservationState
    usuario_id_usuario: int = Field(..., ge=1)
    mesa_id_mesa: int = Field(..., ge=1)

    @field_validator("estado", mode="before")
    @classmethod
    def validate_state(cls, value):
        return ensure_plain_text(value)


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    fecha_hora: datetime | None = None
    estado: ReservationState | None = None
    usuario_id_usuario: int | None = Field(default=None, ge=1)
    mesa_id_mesa: int | None = Field(default=None, ge=1)

    @field_validator("estado", mode="before")
    @classmethod
    def validate_update_state(cls, value):
        return ensure_plain_text(value)


class ReservationRead(ReservationBase):
    id_reserva: int

    model_config = ConfigDict(from_attributes=True)


class ReservationDetailBase(BaseModel):
    cantidad: int = Field(..., ge=1, le=100)
    precio: float = Field(..., ge=0, le=100000)
    producto_id_producto: int = Field(..., ge=1)
    reserva_id_reserva: int = Field(..., ge=1)


class ReservationDetailCreate(ReservationDetailBase):
    pass


class ReservationDetailRead(ReservationDetailBase):
    id_detalleReserva: int

    model_config = ConfigDict(from_attributes=True)

class ReservationCheckoutProductItem(BaseModel):
    id_producto: int = Field(..., ge=1)
    cantidad: int = Field(..., ge=1, le=100)


class ReservationCheckoutRequest(BaseModel):
    date: str = Field(..., pattern=DATE_PATTERN)
    start_time: str = Field(..., pattern=TIME_PATTERN)
    end_time: str = Field(..., pattern=TIME_PATTERN)
    mesa_id: int = Field(..., ge=1)
    productos: list[ReservationCheckoutProductItem] = Field(default_factory=list, max_length=50)
    juego_id: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_schedule(self):
        try:
            start = datetime.strptime(f"{self.date} {self.start_time}", "%Y-%m-%d %H:%M")
            end = datetime.strptime(f"{self.date} {self.end_time}", "%Y-%m-%d %H:%M")
        except ValueError as exc:
            raise ValueError("Fecha u hora invalida.") from exc

        if end <= start:
            raise ValueError("La hora de fin debe ser mayor que la hora de inicio.")

        return self


class ReservationCheckoutResponse(BaseModel):
    message: str
    id_reserva: int


# app/modules/orders/schemas.py

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.validation import ensure_plain_text

OrderType = Literal["Pedido"]
OrderState = Literal["Pendiente", "En Progreso", "Finalizado", "Cancelado"]

class OrderProductInput(BaseModel):
    id_producto: int = Field(..., ge=1)
    cantidad: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    productos: list[OrderProductInput] = Field(..., min_length=1, max_length=50)


class OrderCheckoutResponse(BaseModel):
    message: str
    id_pedido: int


class OrderBase(BaseModel):
    tipo: OrderType
    estado: OrderState
    fecha_hora: datetime
    usuario_id_usuario: int = Field(..., ge=1)
    mesa_id_mesa: int = Field(..., ge=1)

    @field_validator("tipo", "estado", mode="before")
    @classmethod
    def validate_order_text(cls, value):
        return ensure_plain_text(value)


class OrderUpdate(BaseModel):
    tipo: OrderType | None = None
    estado: OrderState | None = None
    fecha_hora: datetime | None = None
    usuario_id_usuario: int | None = Field(default=None, ge=1)
    mesa_id_mesa: int | None = Field(default=None, ge=1)

    @field_validator("tipo", "estado", mode="before")
    @classmethod
    def validate_order_update_text(cls, value):
        return ensure_plain_text(value)


class OrderRead(OrderBase):
    id_pedido: int

    model_config = ConfigDict(from_attributes=True)


class OrderDetailBase(BaseModel):
    cantidad: int = Field(..., ge=1, le=100)
    precio: float = Field(..., ge=0, le=100000)
    producto_id_producto: int = Field(..., ge=1)
    pedido_id_pedido: int = Field(..., ge=1)


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailRead(OrderDetailBase):
    id_detallePed: int

    model_config = ConfigDict(from_attributes=True)

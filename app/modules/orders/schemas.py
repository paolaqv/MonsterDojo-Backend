from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OrderBase(BaseModel):
    tipo: str = Field(..., min_length=1, max_length=50)
    estado: str = Field(..., min_length=1, max_length=50)
    fecha_hora: datetime
    usuario_id_usuario: int
    mesa_id_mesa: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    tipo: str | None = Field(default=None, min_length=1, max_length=50)
    estado: str | None = Field(default=None, min_length=1, max_length=50)
    fecha_hora: datetime | None = None
    usuario_id_usuario: int | None = None
    mesa_id_mesa: int | None = None


class OrderRead(OrderBase):
    id_pedido: int

    model_config = ConfigDict(from_attributes=True)


class OrderDetailBase(BaseModel):
    cantidad: int = Field(..., ge=1)
    precio: float = Field(..., ge=0)
    producto_id_producto: int
    pedido_id_pedido: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetailRead(OrderDetailBase):
    id_detallePed: int

    model_config = ConfigDict(from_attributes=True)
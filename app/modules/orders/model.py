from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.products.model import Producto
    from app.modules.tables.model import Mesa
    from app.modules.users.model import Usuario


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    usuario_id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=False,
    )
    mesa_id_mesa: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mesa.id_mesa"),
        nullable=False,
    )

    detalles_pedido: Mapped[list["DetallePedido"]] = relationship(
        "DetallePedido",
        back_populates="pedido_rel",
        lazy="selectin",
    )

    usuario_rel: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="pedidos",
        lazy="selectin",
    )

    mesa_rel: Mapped["Mesa"] = relationship(
        "Mesa",
        back_populates="pedidos",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Pedido {self.id_pedido}>"


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id_detallePed: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)

    producto_id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("producto.id_producto"),
        nullable=False,
    )
    pedido_id_pedido: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("pedido.id_pedido"),
        nullable=False,
    )

    producto_rel: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="detalles_pedido",
        lazy="selectin",
    )

    pedido_rel: Mapped["Pedido"] = relationship(
        "Pedido",
        back_populates="detalles_pedido",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DetallePedido {self.id_detallePed}>"

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.orders.model import DetallePedido
    from app.modules.reservations.model import DetalleReserva


class CategoriaProducto(Base):
    __tablename__ = "categoria_producto"

    id_catProducto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    productos: Mapped[list["Producto"]] = relationship(
        "Producto",
        back_populates="categoria_producto",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CategoriaProducto {self.nombre}>"


class Producto(Base):
    __tablename__ = "producto"

    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    max_personas: Mapped[int] = mapped_column(Integer, nullable=False)
    imagen: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria_producto_id_catProducto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categoria_producto.id_catProducto"),
        nullable=False,
    )

    categoria_producto: Mapped["CategoriaProducto"] = relationship(
        "CategoriaProducto",
        back_populates="productos",
        lazy="selectin",
    )

    detalles_reserva: Mapped[list["DetalleReserva"]] = relationship(
        "DetalleReserva",
        back_populates="producto_rel",
        lazy="selectin",
    )

    detalles_pedido: Mapped[list["DetallePedido"]] = relationship(
        "DetallePedido",
        back_populates="producto_rel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Producto {self.nombre}>"
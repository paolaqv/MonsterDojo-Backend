from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.model import Usuario
    from app.modules.tables.model import Mesa
    from app.modules.products.model import Producto
    from app.modules.game_rentals.model import RegistroJuego


class Reserva(Base):
    __tablename__ = "reserva"

    id_reserva: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False)

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

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="reservas",
        lazy="selectin",
    )

    mesa: Mapped["Mesa"] = relationship(
        "Mesa",
        back_populates="reservas",
        lazy="selectin",
    )

    detalles_reserva: Mapped[list["DetalleReserva"]] = relationship(
        "DetalleReserva",
        back_populates="reserva_rel",
        lazy="selectin",
    )

    registro_juego: Mapped[list["RegistroJuego"]] = relationship(
        "RegistroJuego",
        back_populates="reserva_rel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Reserva {self.id_reserva}>"


class DetalleReserva(Base):
    __tablename__ = "detalle_reserva"

    id_detalleReserva: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)

    producto_id_producto: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("producto.id_producto"),
        nullable=False,
    )
    reserva_id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reserva.id_reserva"),
        nullable=False,
    )

    producto_rel: Mapped["Producto"] = relationship(
        "Producto",
        back_populates="detalles_reserva",
        lazy="selectin",
    )

    reserva_rel: Mapped["Reserva"] = relationship(
        "Reserva",
        back_populates="detalles_reserva",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DetalleReserva {self.id_detalleReserva}>"
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.orders.model import DetallePedido
    from app.modules.reservations.model import DetalleReserva
    from app.modules.game_rentals.model import RegistroJuego
    from app.modules.users.model import Usuario


class Pago(Base):
    __tablename__ = "pago"

    id_pago: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    monto: Mapped[float] = mapped_column(Float, nullable=False)

    detalle_pedido_id_detallePed: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("detalle_pedido.id_detallePed"),
        nullable=False,
    )
    detalle_reserva_id_detalleReserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("detalle_reserva.id_detalleReserva"),
        nullable=False,
    )
    registro_juego_id_regJuego: Mapped[int] = mapped_column(
        "registro_juego_id_regJuego",
        Integer,
        ForeignKey("registro_juego.id_regJuego"),
        nullable=False,
    )
    usuario_id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=False,
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="pagos",
        lazy="selectin",
    )

    detalle_pedido: Mapped["DetallePedido"] = relationship(
        "DetallePedido",
        lazy="selectin",
    )

    detalle_reserva: Mapped["DetalleReserva"] = relationship(
        "DetalleReserva",
        lazy="selectin",
    )

    registro_juego: Mapped["RegistroJuego"] = relationship(
        "RegistroJuego",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Pago {self.id_pago}>"
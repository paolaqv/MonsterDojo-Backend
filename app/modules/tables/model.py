from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.orders.model import Pedido
    from app.modules.reservations.model import Reserva


class Mesa(Base):
    __tablename__ = "mesa"

    id_mesa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(200), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva",
        back_populates="mesa",
        lazy="selectin",
    )

    pedidos: Mapped[list["Pedido"]] = relationship(
        "Pedido",
        back_populates="mesa_rel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Mesa {self.id_mesa}>"
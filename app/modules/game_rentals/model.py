from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.games.model import Juego
    from app.modules.reservations.model import Reserva
    from app.modules.users.model import Usuario


class RegistroJuego(Base):
    __tablename__ = "registro_juego"

    id_regJuego: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[int] = mapped_column(Integer, nullable=False)

    juego_id_juego: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("juego.id_juego"),
        nullable=False,
    )
    usuario_id_usuario: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=False,
    )
    reserva_id_reserva: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("reserva.id_reserva"),
        nullable=False,
    )

    juego_rel: Mapped["Juego"] = relationship(
        "Juego",
        back_populates="registros_juego",
        lazy="selectin",
    )

    usuario: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="registros_juego",
        lazy="selectin",
    )

    reserva_rel: Mapped["Reserva"] = relationship(
        "Reserva",
        back_populates="registro_juego",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<RegistroJuego {self.id_regJuego}>"
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.game_rentals.model import RegistroJuego


class CategoriaJuego(Base):
    __tablename__ = "categoria_juego"

    id_catJuego: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)

    juegos: Mapped[list["Juego"]] = relationship(
        "Juego",
        back_populates="categoria_juego",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<CategoriaJuego {self.nombre}>"


class Juego(Base):
    __tablename__ = "juego"

    id_juego: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    precio_alquiler: Mapped[float] = mapped_column(Float, nullable=False)
    precio_venta: Mapped[float] = mapped_column(Float, nullable=False)
    disponible_venta: Mapped[bool] = mapped_column(Boolean, nullable=False)
    imagen: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria_juego_id_catJuego: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("categoria_juego.id_catJuego"),
        nullable=False,
    )

    categoria_juego: Mapped["CategoriaJuego"] = relationship(
        "CategoriaJuego",
        back_populates="juegos",
        lazy="selectin",
    )

    registros_juego: Mapped[list["RegistroJuego"]] = relationship(
        "RegistroJuego",
        back_populates="juego_rel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Juego {self.nombre}>"
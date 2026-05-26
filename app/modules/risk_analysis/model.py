from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.users.model import Usuario


class Activo(Base):
    __tablename__ = "activo"

    id_activo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String, nullable=False)
    propietario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id_usuario", ondelete="SET NULL"), nullable=True)

    propietario: Mapped["Usuario | None"] = relationship("Usuario", lazy="selectin")
    riesgos: Mapped[list["Riesgo"]] = relationship("Riesgo", back_populates="activo", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Activo {self.nombre}>"


class Riesgo(Base):
    __tablename__ = "riesgo"

    id_riesgo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activo_id_activo: Mapped[int] = mapped_column(Integer, ForeignKey("activo.id_activo", ondelete="CASCADE"), nullable=False)
    amenaza: Mapped[str] = mapped_column(String, nullable=False)
    consecuencia: Mapped[str] = mapped_column(Text, nullable=False)
    probabilidad: Mapped[int] = mapped_column(Integer, nullable=False)
    impacto: Mapped[int] = mapped_column(Integer, nullable=False)
    riesgo_inherente: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_inherente: Mapped[str] = mapped_column(String(50), nullable=False)
    tratamiento: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_registro: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, server_default=func.now())

    activo: Mapped["Activo"] = relationship("Activo", back_populates="riesgos", lazy="selectin")
    mitigaciones: Mapped[list["Mitigacion"]] = relationship("Mitigacion", back_populates="riesgo", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Riesgo {self.amenaza}>"


class Mitigacion(Base):
    __tablename__ = "mitigacion"

    id_mitigacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    riesgo_id_riesgo: Mapped[int] = mapped_column(Integer, ForeignKey("riesgo.id_riesgo", ondelete="CASCADE"), nullable=False)
    control_implementado: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)
    nivel: Mapped[str] = mapped_column(String(2), nullable=False)
    frecuencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    probabilidad_residual: Mapped[int] = mapped_column(Integer, nullable=False)
    impacto_residual: Mapped[int] = mapped_column(Integer, nullable=False)
    riesgo_residual: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_residual: Mapped[str] = mapped_column(String(50), nullable=False)

    riesgo: Mapped["Riesgo"] = relationship("Riesgo", back_populates="mitigaciones", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Mitigacion {self.control_implementado[:30]}>"
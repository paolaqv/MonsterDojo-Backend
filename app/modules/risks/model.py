from __future__ import annotations
from datetime import datetime
from sqlalchemy import Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Activo(Base):
    __tablename__ = "activo"

    id_activo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    
    propietario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)

    riesgos: Mapped[list["Riesgo"]] = relationship("Riesgo", back_populates="activo", cascade="all, delete-orphan")


class Riesgo(Base):
    __tablename__ = "riesgo"

    id_riesgo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    activo_id_activo: Mapped[int] = mapped_column(Integer, ForeignKey("activo.id_activo"), nullable=False)
    
    amenaza: Mapped[str] = mapped_column(String(255), nullable=False)
    consecuencia: Mapped[str] = mapped_column(Text, nullable=False)
    
    probabilidad: Mapped[int] = mapped_column(Integer, nullable=False)
    impacto: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # --- NUEVOS CAMPOS INHERENTES (Requeridos por RiskAnalysisView.vue) ---
    riesgo_inherente: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_inherente: Mapped[str] = mapped_column(String(50), nullable=False)
    # ----------------------------------------------------------------------

    tratamiento: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    activo: Mapped["Activo"] = relationship("Activo", back_populates="riesgos")
    mitigaciones: Mapped[list["Mitigacion"]] = relationship("Mitigacion", back_populates="riesgo", cascade="all, delete-orphan")


class Mitigacion(Base):
    __tablename__ = "mitigacion"

    id_mitigacion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    riesgo_id_riesgo: Mapped[int] = mapped_column(Integer, ForeignKey("riesgo.id_riesgo"), nullable=False)
    
    control_implementado: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Ajustado a las opciones del UI (T/P) y (A/B)
    tipo: Mapped[str] = mapped_column(String(2), nullable=False)
    nivel: Mapped[str] = mapped_column(String(2), nullable=False)
    
    # Nuevo campo (Opcional en el UI)
    frecuencia: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    probabilidad_residual: Mapped[int] = mapped_column(Integer, nullable=False)
    impacto_residual: Mapped[int] = mapped_column(Integer, nullable=False)

    # --- NUEVOS CAMPOS RESIDUALES (Enviados en el payload) ---
    riesgo_residual: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_residual: Mapped[str] = mapped_column(String(50), nullable=False)
    # ---------------------------------------------------------

    riesgo: Mapped["Riesgo"] = relationship("Riesgo", back_populates="mitigaciones")
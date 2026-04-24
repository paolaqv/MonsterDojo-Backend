from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PoliticaPassword(Base):
    __tablename__ = "politica_password"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    longitud_minima: Mapped[int] = mapped_column(Integer, nullable=False, default=8)
    dias_expiracion: Mapped[int] = mapped_column(Integer, nullable=False, default=90)
    periodo_no_reutilizacion_meses: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    requiere_mayusculas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requiere_minusculas: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requiere_numeros: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requiere_simbolos: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    max_intentos_login: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actualizado_por_usuario_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=True,
    )


class HistorialPassword(Base):
    __tablename__ = "historial_password"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    fecha_cambio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_token"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
        nullable=False,
    )
    codigo_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    usado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
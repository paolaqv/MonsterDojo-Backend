from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.base import Base

if TYPE_CHECKING:
    from app.logs.activity.model import RegistroActividad
    from app.modules.game_rentals.model import RegistroJuego
    from app.modules.orders.model import Pedido
    from app.modules.payments.model import Pago
    from app.modules.reservations.model import Reserva


class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    usuarios: Mapped[list["Usuario"]] = relationship(
        "Usuario",
        back_populates="rol",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Rol {self.nombre}>"


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    nombre: Mapped[str] = mapped_column(String(50), nullable=False)
    primer_apellido: Mapped[str | None] = mapped_column(String(50), nullable=True)
    segundo_apellido: Mapped[str | None] = mapped_column(String(50), nullable=True)

    correo: Mapped[str] = mapped_column(String(100), nullable=False)
    telefono: Mapped[int | None] = mapped_column(Integer, nullable=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pregunta_seguridad: Mapped[str] = mapped_column(String(255), nullable=False, default="temporal")
    respuesta_seguridad: Mapped[str] = mapped_column(String(255), nullable=False, default="temporal")
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fecha_bloqueo: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fecha_ultimo_cambio_password: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_expiracion_password: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requiere_cambio_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    rol_id_rol: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("rol.id_rol"),
        nullable=False,
    )

    rol: Mapped["Rol"] = relationship(
        "Rol",
        back_populates="usuarios",
        lazy="selectin",
    )

    pagos: Mapped[list["Pago"]] = relationship(
        "Pago",
        back_populates="usuario",
        lazy="selectin",
    )

    registros_juego: Mapped[list["RegistroJuego"]] = relationship(
        "RegistroJuego",
        back_populates="usuario",
        lazy="selectin",
    )

    reservas: Mapped[list["Reserva"]] = relationship(
        "Reserva",
        back_populates="usuario",
        lazy="selectin",
    )

    actividades: Mapped[list["RegistroActividad"]] = relationship(
        "RegistroActividad",
        back_populates="usuario",
        lazy="selectin",
    )

    pedidos: Mapped[list["Pedido"]] = relationship(
        "Pedido",
        back_populates="usuario_rel",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.correo}>"

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class RegistroAplicacion(Base):
    __tablename__ = "registro_aplicacion"

    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime(timezone=True), server_default=func.now())

    modulo = Column(String(100), nullable=False)
    evento = Column(String(255), nullable=False)
    descripcion = Column(Text)

    severidad = Column(String(20), default="INFO")

    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id_usuario"),
        nullable=True,
    )

    entidad_afectada = Column(String(100))
    entidad_id = Column(Integer)

    estado = Column(String(20), default="OK")

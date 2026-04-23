from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.db.base import Base


class RegistroActividad(Base):
    __tablename__ = "registro_actividad"

    id = Column(Integer, primary_key=True, index=True)

    usuario_id = Column(Integer, nullable=True)
    rol_id = Column(String(50), nullable=True)

    evento = Column(String(80), nullable=False)
    modulo = Column(String(50), nullable=False)

    accion = Column(String(30))
    descripcion = Column(Text)

    ip_origen = Column(String(45))
    user_agent = Column(Text)

    estado = Column(String(20))
    severidad = Column(String(20))

    entidad_afectada = Column(String(50))
    entidad_id = Column(Integer)

    valor_anterior = Column(JSONB)
    valor_nuevo = Column(JSONB)

    fecha = Column(DateTime(timezone=True), server_default=func.now())
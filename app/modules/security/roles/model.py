from sqlalchemy import Boolean, Column, ForeignKey, String
from app.db.base import Base


class Permiso(Base):
    __tablename__ = "permiso"

    id_permiso = Column(String(60), primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    modulo = Column(String(50), nullable=False)
    descripcion = Column(String(255), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)


class RolPermiso(Base):
    __tablename__ = "rol_permiso"

    rol_id_rol = Column(String(50), ForeignKey("rol.id_rol"), primary_key=True)
    permiso_id_permiso = Column(String(60), ForeignKey("permiso.id_permiso"), primary_key=True)
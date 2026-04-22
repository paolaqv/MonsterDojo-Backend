from pydantic import BaseModel
from typing import List, Optional


class PermissionRead(BaseModel):
    id_permiso: str
    nombre: str
    modulo: str
    descripcion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True


class RolePermissionUpdate(BaseModel):
    permisos: List[str]


class RoleRead(BaseModel):
    id_rol: str
    nombre: str
    activo: bool = True
    permisos: List[str] = []


class RoleCreate(BaseModel):
    id_rol: str
    nombre: str
    activo: bool = True
    permisos: List[str] = []


class RoleUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None
    permisos: Optional[List[str]] = None


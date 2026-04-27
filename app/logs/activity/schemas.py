from pydantic import BaseModel
from typing import Optional, Dict, Any


class ActivityLogCreate(BaseModel):

    usuario_id: Optional[int] = None
    rol_id: Optional[str] = None

    evento: str
    modulo: str

    accion: Optional[str]=None
    descripcion: Optional[str]=None

    ip_origen: Optional[str]=None
    user_agent: Optional[str]=None

    estado: Optional[str]=None
    severidad: Optional[str]=None

    entidad_afectada: Optional[str]=None
    entidad_id: Optional[int]=None

    valor_anterior: Optional[Dict[str,Any]]=None
    valor_nuevo: Optional[Dict[str,Any]]=None


class ActivityLogOut(ActivityLogCreate):
    id:int

    class Config:
        from_attributes=True
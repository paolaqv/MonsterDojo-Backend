from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.application.repository import obtener_logs_aplicacion
from app.logs.application.schemas import ApplicationLogOut
from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario
from app.shared.validation import sanitize_plain_text

router = APIRouter(
    prefix="/logs/application",
    tags=["Auditoria"],
)


@router.get("/", response_model=list[ApplicationLogOut])
def ver_logs_aplicacion(
    severidad: Literal["INFO", "WARN", "ERROR", "CRITICA"] | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    modulo: str | None = Query(default=None, max_length=100),
    estado: str | None = Query(default=None, max_length=20),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return obtener_logs_aplicacion(
        db,
        severidad=severidad,
        search=sanitize_plain_text(search) if search else None,
        modulo=sanitize_plain_text(modulo) if modulo else None,
        estado=sanitize_plain_text(estado) if estado else None,
        skip=skip,
        limit=limit,
    )

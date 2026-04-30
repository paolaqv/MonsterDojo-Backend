from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.activity.repository import obtener_logs
from app.logs.activity.schemas import ActivityLogOut
from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario
from app.shared.validation import sanitize_plain_text

router = APIRouter(
    prefix="/logs",
    tags=["Auditoria"],
)


@router.get("/", response_model=list[ActivityLogOut])
def ver_logs(
    severidad: Literal["BAJA", "MEDIA", "ALTA", "CRITICA"] | None = Query(default=None),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    critical_only: bool = Query(default=False),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return obtener_logs(
        db,
        severidad=severidad,
        search=sanitize_plain_text(search) if search else None,
        critical_only=critical_only,
        skip=skip,
        limit=limit,
    )

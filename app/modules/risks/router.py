from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.permissions import require_permissions
from app.modules.users.model import Usuario
from . import schemas, service

router = APIRouter(
    prefix="/risks",
    tags=["Risk Management"]
)

# --- ACTIVOS ---
@router.get("/activos/", response_model=list[schemas.ActivoRead])
def read_activos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")), # Asumiendo que seguridad gestiona esto
):
    return service.get_activos(db, skip=skip, limit=limit)

@router.post("/activos/", response_model=schemas.ActivoRead, status_code=status.HTTP_201_CREATED)
def create_new_activo(
    payload: schemas.ActivoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    return service.create_activo(db, payload)

@router.put("/activos/{activo_id}", response_model=schemas.ActivoRead)
def update_existing_activo(
    activo_id: int,
    payload: schemas.ActivoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        return service.update_activo(db, activo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/activos/{activo_id}")
def delete_existing_activo(
    activo_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        service.delete_activo(db, activo_id)
        return {"message": "Activo eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- RIESGOS ---
@router.get("/riesgos/", response_model=list[schemas.RiesgoRead])
def read_riesgos(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=500, ge=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    return service.get_riesgos(db, skip=skip, limit=limit)

@router.post("/riesgos/", response_model=schemas.RiesgoRead, status_code=status.HTTP_201_CREATED)
def create_new_riesgo(
    payload: schemas.RiesgoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        return service.create_riesgo(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/riesgos/{riesgo_id}", response_model=schemas.RiesgoRead)
def update_existing_riesgo(
    riesgo_id: int,
    payload: schemas.RiesgoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        return service.update_riesgo(db, riesgo_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/riesgos/{riesgo_id}")
def delete_existing_riesgo(
    riesgo_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        service.delete_riesgo(db, riesgo_id)
        return {"message": "Riesgo eliminado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- MITIGACIONES ---
@router.get("/mitigaciones/", response_model=list[schemas.MitigacionRead])
def read_mitigaciones(
    riesgo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    return service.get_mitigaciones(db, riesgo_id)

@router.post("/mitigaciones/", response_model=schemas.MitigacionRead, status_code=status.HTTP_201_CREATED)
def create_new_mitigacion(
    payload: schemas.MitigacionCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        return service.create_mitigacion(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/mitigaciones/{mitigacion_id}", response_model=schemas.MitigacionRead)
def update_existing_mitigacion(
    mitigacion_id: int,
    payload: schemas.MitigacionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        return service.update_mitigacion(db, mitigacion_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.delete("/mitigaciones/{mitigacion_id}")
def delete_existing_mitigacion(
    mitigacion_id: int, 
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_auditoria")),
):
    try:
        service.delete_mitigacion(db, mitigacion_id)
        return {"message": "Mitigación eliminada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
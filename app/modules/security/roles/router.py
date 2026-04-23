from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario
from app.modules.security.roles.schemas import PermissionRead, RoleCreate, RoleRead, RoleUpdate
from app.modules.security.roles.service import (
    create_role,
    delete_role,
    get_all_permissions,
    get_all_roles,
    get_role_by_id,
    update_role,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=list[RoleRead])
def read_roles(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return get_all_roles(db)


@router.get("/permissions", response_model=list[PermissionRead])
def read_permissions(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return get_all_permissions(db)


@router.get("/{role_id}", response_model=RoleRead)
def read_role(
    role_id: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado.")
    return role


@router.post("/", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_new_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        return create_role(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{role_id}", response_model=RoleRead)
def update_existing_role(
    role_id: str,
    payload: RoleUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        return update_role(db, role_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{role_id}", status_code=status.HTTP_200_OK)
def delete_existing_role(
    role_id: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        delete_role(db, role_id)
        return {"message": "Rol eliminado correctamente."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
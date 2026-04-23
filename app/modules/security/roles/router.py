from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario

from app.modules.security.roles.schemas import (
    PermissionRead,
    RoleCreate,
    RoleRead,
    RoleUpdate
)

from app.modules.security.roles.service import (
    create_role,
    delete_role,
    get_all_permissions,
    get_all_roles,
    get_role_by_id,
    update_role
)


router=APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("/",response_model=list[RoleRead])
def read_roles(
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    return get_all_roles(db)


@router.get("/permissions",response_model=list[PermissionRead])
def read_permissions(
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    return get_all_permissions(db)


@router.get("/{role_id}",response_model=RoleRead)
def read_role(
    role_id:str,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    role=get_role_by_id(db,role_id)

    if not role:
        raise HTTPException(
            status_code=404,
            detail="Rol no encontrado."
        )

    return role


@router.post("/",response_model=RoleRead,status_code=201)
def create_new_role(
    payload:RoleCreate,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        role=create_role(
            db,
            payload
        )

        registrar_evento(
            db=db,
            evento="ROL_CREADO",
            modulo="roles",
            accion="CREATE",
            estado="OK",
            severidad="ALTA",
            entidad_afectada="rol"
        )

        return role

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{role_id}",response_model=RoleRead)
def update_existing_role(
    role_id:str,
    payload:RoleUpdate,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        role=update_role(
            db,
            role_id,
            payload
        )

        registrar_evento(
            db=db,
            evento="ROL_EDITADO",
            modulo="roles",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            entidad_afectada="rol"
        )

        return role

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{role_id}",status_code=200)
def delete_existing_role(
    role_id:str,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        delete_role(
            db,
            role_id
        )

        registrar_evento(
            db=db,
            evento="ROL_ELIMINADO",
            modulo="roles",
            accion="DELETE",
            estado="OK",
            severidad="CRITICA",
            entidad_afectada="rol"
        )

        return {
            "message":"Rol eliminado correctamente."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.permissions import require_permissions
from app.modules.users.model import Usuario


def _role_field(role, field):
    # El servicio de roles devuelve diccionarios (no objetos ORM); se admite
    # también un objeto por robustez ante cambios futuros.
    if role is None:
        return None
    if isinstance(role, dict):
        return role.get(field)
    return getattr(role, field, None)


def _role_snapshot(role) -> dict | None:
    if role is None:
        return None
    return {
        "id_rol": _role_field(role, "id_rol"),
        "nombre": _role_field(role, "nombre"),
        "activo": _role_field(role, "activo"),
    }

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

#mediacion completa: roles validados por permisos
router=APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


@router.get("/",response_model=list[RoleRead])
def read_roles(
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_usuarios"))
):
    return get_all_roles(db)


@router.get("/permissions",response_model=list[PermissionRead])
def read_permissions(
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_usuarios"))
):
    return get_all_permissions(db)


@router.get("/{role_id}",response_model=RoleRead)
def read_role(
    role_id:str,
    db:Session=Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_usuarios"))
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
    current_user: Usuario = Depends(
        require_permissions("gestionar_roles")
    )
):
    try:

        role=create_role(
            db,
            payload
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ROL_CREADO",
            modulo="roles",
            accion="CREATE",
            estado="OK",
            severidad="ALTA",
            descripcion=f"Encargado {current_user.id_usuario} creo rol '{_role_field(role, 'nombre')}' (id {_role_field(role, 'id_rol')}).",
            entidad_afectada="rol",
            entidad_id=None,
            valor_nuevo=_role_snapshot(role),
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
    current_user: Usuario = Depends(
        require_permissions("gestionar_roles")
    )
):
    try:
        previous_role = get_role_by_id(db, role_id)
        previous_snapshot = _role_snapshot(previous_role)

        role=update_role(
            db,
            role_id,
            payload
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ROL_EDITADO",
            modulo="roles",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            descripcion=f"Encargado {current_user.id_usuario} edito rol '{_role_field(role, 'nombre')}' (id {_role_field(role, 'id_rol')}).",
            entidad_afectada="rol",
            valor_anterior=previous_snapshot,
            valor_nuevo=_role_snapshot(role),
        )

        return role

    except ValueError as e:

        detail=str(e)
        status_code=(
            status.HTTP_404_NOT_FOUND
            if detail=="Rol no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )


@router.delete("/{role_id}",status_code=200)
def delete_existing_role(
    role_id:str,
    db:Session=Depends(get_db),
    current_user: Usuario = Depends(
        require_permissions("gestionar_roles")
    )
):
    try:
        previous_role = get_role_by_id(db, role_id)
        previous_snapshot = _role_snapshot(previous_role)
        nombre_legible = _role_field(previous_role, "nombre") or role_id

        delete_role(
            db,
            role_id
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ROL_ELIMINADO",
            modulo="roles",
            accion="DELETE",
            estado="OK",
            severidad="CRITICA",
            descripcion=f"Encargado {current_user.id_usuario} elimino rol '{nombre_legible}' (id {role_id}).",
            entidad_afectada="rol",
            valor_anterior=previous_snapshot,
        )

        return {
            "message":"Rol eliminado correctamente."
        }

    except ValueError as e:

        detail=str(e)
        status_code=(
            status.HTTP_404_NOT_FOUND
            if detail=="Rol no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )

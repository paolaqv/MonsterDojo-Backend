from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.modules.auth.schemas import MessageResponse
from app.modules.security.passwords.service import unlock_user
from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.permissions import require_roles
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserRead, UserRoleUpdate, UserStatusUpdate, UserUpdate, UserCreate

from app.modules.users.service import (
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
    update_user_role,
    update_user_status,
    create_user
)


router = APIRouter(
    prefix="/security/users",
    tags=["Security Users"],
)


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    return get_all_users(db)


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id:int,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    user=get_user_by_id(db,user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado."
        )

    return user


@router.put("/{user_id}",response_model=UserRead)
def update_security_user(
    user_id:int,
    payload:UserUpdate,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        user=update_user(
            db,
            user_id,
            payload
        )

        registrar_evento(
            db=db,
            evento="USUARIO_EDITADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="MEDIA",
            entidad_afectada="usuario",
            entidad_id=user_id
        )

        return user

    except ValueError as e:

        detail=str(e)

        status_code=(
            status.HTTP_404_NOT_FOUND
            if detail=="Usuario no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )


@router.put("/{user_id}/role",response_model=UserRead)
def update_security_user_role(
    user_id:int,
    payload:UserRoleUpdate,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        user=update_user_role(
            db,
            user_id,
            payload.rol_id_rol
        )

        registrar_evento(
            db=db,
            evento="ROL_CAMBIADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",

            entidad_afectada="usuario",
            entidad_id=user_id,

            valor_nuevo={
                "nuevo_rol":payload.rol_id_rol
            }
        )

        return user

    except ValueError as e:

        detail=str(e)

        status_code=(
            status.HTTP_404_NOT_FOUND
            if detail=="Usuario no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )

        raise HTTPException(
            status_code=status_code,
            detail=detail
        )


@router.patch("/{user_id}/status",response_model=UserRead)
def update_security_user_status(
    user_id:int,
    payload:UserStatusUpdate,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        user=update_user_status(
            db,
            user_id,
            payload.activo
        )

        registrar_evento(
            db=db,
            evento="USUARIO_ESTADO_CAMBIADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            entidad_afectada="usuario",
            entidad_id=user_id,
            valor_nuevo={
                "activo":payload.activo
            }
        )

        return user

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{user_id}",status_code=200)
def delete_security_user(
    user_id:int,
    db:Session=Depends(get_db),
    _:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:

        delete_user(
            db,
            user_id
        )

        registrar_evento(
            db=db,
            evento="USUARIO_ELIMINADO",
            modulo="usuarios",
            accion="DELETE",
            estado="OK",
            severidad="CRITICA",
            entidad_afectada="usuario",
            entidad_id=user_id
        )

        return {
            "message":"Usuario eliminado correctamente."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_security_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    try:
        return create_user(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@router.post("/{user_id}/unlock", response_model=MessageResponse)
def unlock_security_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    unlock_user(db, user)
    return {"message": "Usuario desbloqueado correctamente."}

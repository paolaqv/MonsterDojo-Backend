from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.logs.activity.service import registrar_evento

from app.modules.auth.permissions import require_roles
from app.modules.auth.schemas import MessageResponse
from app.modules.security.passwords.service import unlock_user
from app.modules.users.model import Usuario
from app.modules.users.schemas import UserCreate, UserRead, UserRoleUpdate, UserStatusUpdate, UserUpdate
from app.modules.users.service import (
    create_user,
    delete_user,
    get_all_users,
    get_user_by_id,
    update_user,
    update_user_role,
    update_user_status,
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


@router.put("/{user_id}", response_model=UserRead)
def update_security_user(
    user_id:int,
    payload:UserUpdate,
    db:Session=Depends(get_db),
    current_user:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:
        if user_id == current_user.id_usuario and payload.rol_id_rol != current_user.rol_id_rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cambiar tu propio rol desde este flujo.",
            )

        previous_user = get_user_by_id(db, user_id)
        valor_anterior = None
        if previous_user:
            valor_anterior = {
                "nombre": previous_user.nombre,
                "correo": previous_user.correo,
                "rol_id_rol": previous_user.rol_id_rol,
                "activo": previous_user.activo,
            }

        user=update_user(
            db,
            user_id,
            payload
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="USUARIO_EDITADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="MEDIA",
            entidad_afectada="usuario",
            entidad_id=user_id,
            valor_anterior=valor_anterior,
            valor_nuevo={
                "nombre": user.nombre,
                "correo": user.correo,
                "rol_id_rol": user.rol_id_rol,
                "activo": user.activo,
            },
        )

        return user

    except ValueError as e:

        detail=str(e)

        status_code=(
            status.HTTP_404_NOT_FOUND
            if detail=="Usuario no encontrado."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=detail)



@router.put("/{user_id}/role",response_model=UserRead)
def update_security_user_role(
    user_id:int,
    payload:UserRoleUpdate,
    db:Session=Depends(get_db),
    current_user:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:
        if user_id == current_user.id_usuario and payload.activo is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario.",
            )

        previous_user = get_user_by_id(db, user_id)
        previous_role = previous_user.rol_id_rol if previous_user else None

        user=update_user_role(
            db,
            user_id,
            payload.rol_id_rol
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="ROL_CAMBIADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",

            entidad_afectada="usuario",
            entidad_id=user_id,

            valor_anterior={
                "rol_anterior":previous_role
            },
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
    current_user:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:
        if user_id == current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminar tu propio usuario.",
            )

        previous_user = get_user_by_id(db, user_id)
        previous_status = previous_user.activo if previous_user else None

        user=update_user_status(
            db,
            user_id,
            payload.activo
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="USUARIO_ESTADO_CAMBIADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="ALTA",
            entidad_afectada="usuario",
            entidad_id=user_id,
            valor_anterior={
                "activo":previous_status
            },
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


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_security_user(
    user_id:int,
    db:Session=Depends(get_db),
    current_user:Usuario=Depends(require_roles("encargadoSeguridad"))
):
    try:
        if (
            user_id == current_user.id_usuario
            and payload.rol_id_rol is not None
            and payload.rol_id_rol != current_user.rol_id_rol
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes cambiar tu propio rol desde este flujo.",
            )

        if user_id == current_user.id_usuario and payload.activo is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes desactivar tu propio usuario.",
            )

        previous_user = get_user_by_id(db, user_id)
        valor_anterior = None
        if previous_user:
            valor_anterior = {
                "nombre": previous_user.nombre,
                "correo": previous_user.correo,
                "rol_id_rol": previous_user.rol_id_rol,
                "activo": previous_user.activo,
            }

        delete_user(
            db,
            user_id
        )

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="USUARIO_ELIMINADO",
            modulo="usuarios",
            accion="DELETE",
            estado="OK",
            severidad="CRITICA",
            entidad_afectada="usuario",
            entidad_id=user_id,
            valor_anterior=valor_anterior,
        )

        return {
            "message":"Usuario eliminado correctamente."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/{user_id}/send-credentials", response_model=MessageResponse)
def send_credentials_placeholder(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    return {"message": "La solicitud de envío de credenciales fue registrada."}


@router.post("/{user_id}/unlock", response_model=MessageResponse)
def unlock_security_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("encargadoSeguridad")),
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
        )

    unlock_user(db, user)
    registrar_evento(
        db=db,
        usuario_id=current_user.id_usuario,
        rol_id=current_user.rol_id_rol,
        evento="USUARIO_DESBLOQUEADO",
        modulo="usuarios",
        accion="UPDATE",
        estado="OK",
        severidad="ALTA",
        entidad_afectada="usuario",
        entidad_id=user_id,
        valor_anterior={"bloqueado": True},
        valor_nuevo={"bloqueado": False},
    )
    return {"message": "Usuario desbloqueado correctamente."}

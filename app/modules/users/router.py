from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.modules.auth.permissions import require_roles
from app.db.session import get_db
from app.logs.activity.service import registrar_evento
from app.modules.auth.dependencies import get_current_user
from app.modules.users.model import Usuario
from app.modules.users.schemas import CurrentUserWithPermissionsRead, UserRead, UserUpdateSelf
from app.modules.users.service import get_user_permissions, update_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=CurrentUserWithPermissionsRead)
def read_current_user(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    permisos = get_user_permissions(db, current_user.id_usuario)

    return {
        **current_user.__dict__,
        "permisos": permisos,
    }

@router.put("/me/profile", response_model=UserRead)
def update_me(
    payload: UserUpdateSelf,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    try:
        valor_anterior = {
            "nombre": current_user.nombre,
            "correo_contacto": getattr(current_user, "correo_contacto", None),
        }

        updated = update_current_user(db, current_user, payload)

        registrar_evento(
            db=db,
            usuario_id=current_user.id_usuario,
            rol_id=current_user.rol_id_rol,
            evento="PERFIL_ACTUALIZADO",
            modulo="usuarios",
            accion="UPDATE",
            estado="OK",
            severidad="MEDIA",
            descripcion=f"Usuario {current_user.id_usuario} ({current_user.correo}) actualizo su propio perfil.",
            entidad_afectada="usuario",
            entidad_id=current_user.id_usuario,
            valor_anterior=valor_anterior,
            valor_nuevo={
                "nombre": updated.nombre,
                "correo_contacto": getattr(updated, "correo_contacto", None),
            },
        )

        return updated
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
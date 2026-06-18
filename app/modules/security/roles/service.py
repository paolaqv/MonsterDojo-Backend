from sqlalchemy.orm import Session
from app.modules.users.model import Rol, Usuario
from app.modules.security.roles.model import Permiso, RolPermiso

#mediacion completa, evitar permisos inactivos a roles
def _validate_permission_ids(db: Session, permission_ids: list[str]) -> None:
    if not permission_ids:
        return

    existing = {
        permission.id_permiso
        for permission in db.query(Permiso)
        .filter(
            Permiso.id_permiso.in_(permission_ids),
            Permiso.activo.is_(True),
        )
        .all()
    }

    missing_or_inactive = sorted(set(permission_ids) - existing)
    if missing_or_inactive:
        raise ValueError(
            f"Permisos inexistentes o inactivos: {', '.join(missing_or_inactive)}."
        )


def _assert_unique_permission_set(
    db: Session,
    permission_ids: list[str],
    exclude_role_id: str | None = None,
) -> None:
    """Impide que existan dos roles con exactamente el mismo conjunto de accesos.

    No se valida el conjunto vacío para no bloquear roles de sistema sin
    permisos (por ejemplo, el rol por defecto "sin_rol").
    """
    target = frozenset(pid for pid in (permission_ids or []) if pid)
    if not target:
        return

    for role in db.query(Rol).all():
        if exclude_role_id is not None and role.id_rol == exclude_role_id:
            continue

        existing_permisos = frozenset(
            rp.permiso_id_permiso
            for rp in db.query(RolPermiso.permiso_id_permiso)
            .filter(RolPermiso.rol_id_rol == role.id_rol)
            .all()
        )

        if existing_permisos == target:
            raise ValueError(
                f"Ya existe un rol con los mismos accesos: '{role.nombre}' "
                f"(ID: {role.id_rol}). No puedes registrar roles duplicados; "
                f"modifica los permisos o edita el rol existente."
            )

def get_all_permissions(db: Session):
    return (
        db.query(Permiso)
        .filter(Permiso.activo.is_(True))
        .all()
    )

def get_all_roles(db: Session):
    roles = db.query(Rol).all()
    result = []

    for role in roles:
        permisos = (
            db.query(RolPermiso.permiso_id_permiso)
            .filter(RolPermiso.rol_id_rol == role.id_rol)
            .all()
        )

        result.append({
            "id_rol": role.id_rol,
            "nombre": role.nombre,
            "activo": role.activo,
            "permisos": [p.permiso_id_permiso for p in permisos],
        })

    return result


def get_role_by_id(db: Session, role_id: str):
    role = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if not role:
        return None

    permisos = (
        db.query(RolPermiso.permiso_id_permiso)
        .filter(RolPermiso.rol_id_rol == role.id_rol)
        .all()
    )

    return {
        "id_rol": role.id_rol,
        "nombre": role.nombre,
        "activo": role.activo,
        "permisos": [p.permiso_id_permiso for p in permisos],
    }


def create_role(db: Session, payload):
    role_id = payload.id_rol.strip()
    role_name = payload.nombre.strip()
    permisos = payload.permisos or []

    existing = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if existing:
        raise ValueError("El rol ya existe.")

    _validate_permission_ids(db, permisos)
    _assert_unique_permission_set(db, permisos)

    role = Rol(
        id_rol=role_id,
        nombre=role_name,
        activo=payload.activo,
    )

    try:
        db.add(role)

        db.flush()
        for permiso_id in permisos:
            db.add(
                RolPermiso(
                    rol_id_rol=role_id,
                    permiso_id_permiso=permiso_id,
                )
            )

        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_role_by_id(db, role_id)


def update_role(db: Session, role_id: str, payload):
    role = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if not role:
        raise ValueError("Rol no encontrado.")

    if payload.nombre is not None:
        role.nombre = payload.nombre

    if payload.activo is not None:
        role.activo = payload.activo

    if payload.permisos is not None:
        _validate_permission_ids(db, payload.permisos)
        _assert_unique_permission_set(db, payload.permisos, exclude_role_id=role_id)

    try:
        if payload.permisos is not None:
            db.query(RolPermiso).filter(RolPermiso.rol_id_rol == role_id).delete()

            for permiso_id in payload.permisos:
                db.add(RolPermiso(
                    rol_id_rol=role_id,
                    permiso_id_permiso=permiso_id,
                ))

        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_role_by_id(db, role_id)


def delete_role(db: Session, role_id: str):
    role = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if not role:
        raise ValueError("Rol no encontrado.")

    assigned_users = db.query(Usuario).filter(Usuario.rol_id_rol == role_id).count()
    if assigned_users:
        raise ValueError("No se puede eliminar un rol asignado a usuarios.")

    db.query(RolPermiso).filter(RolPermiso.rol_id_rol == role_id).delete()
    db.delete(role)
    db.commit()


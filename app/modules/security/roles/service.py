from sqlalchemy.orm import Session
from app.modules.users.model import Rol
from app.modules.security.roles.model import Permiso, RolPermiso
def get_all_permissions(db: Session):
    return db.query(Permiso).all()


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
    existing = db.query(Rol).filter(Rol.id_rol == payload.id_rol).first()
    if existing:
        raise ValueError("El rol ya existe.")

    role = Rol(
        id_rol=payload.id_rol,
        nombre=payload.nombre,
        activo=payload.activo,
    )

    db.add(role)
    db.commit()

    for permiso_id in payload.permisos:
        db.add(RolPermiso(
            rol_id_rol=payload.id_rol,
            permiso_id_permiso=permiso_id,
        ))

    db.commit()
    return get_role_by_id(db, payload.id_rol)


def update_role(db: Session, role_id: str, payload):
    role = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if not role:
        raise ValueError("Rol no encontrado.")

    if payload.nombre is not None:
        role.nombre = payload.nombre

    if payload.activo is not None:
        role.activo = payload.activo

    db.commit()

    if payload.permisos is not None:
        db.query(RolPermiso).filter(RolPermiso.rol_id_rol == role_id).delete()
        db.commit()

        for permiso_id in payload.permisos:
            db.add(RolPermiso(
                rol_id_rol=role_id,
                permiso_id_permiso=permiso_id,
            ))
        db.commit()

    return get_role_by_id(db, role_id)


def delete_role(db: Session, role_id: str):
    role = db.query(Rol).filter(Rol.id_rol == role_id).first()
    if not role:
        raise ValueError("Rol no encontrado.")

    db.query(RolPermiso).filter(RolPermiso.rol_id_rol == role_id).delete()
    db.delete(role)
    db.commit()


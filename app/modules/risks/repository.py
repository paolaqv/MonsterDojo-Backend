from sqlalchemy import select
from sqlalchemy.orm import Session
from .model import Activo, Riesgo, Mitigacion
from .schemas import ActivoCreate, ActivoUpdate, RiesgoCreate, RiesgoUpdate, MitigacionCreate, MitigacionUpdate

# --- ACTIVOS ---
def get_activos(db: Session, skip: int = 0, limit: int = 100) -> list[Activo]:
    stmt = select(Activo).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())

def get_activo_by_id(db: Session, activo_id: int) -> Activo | None:
    stmt = select(Activo).where(Activo.id_activo == activo_id)
    return db.scalar(stmt)

def create_activo(db: Session, activo_data: ActivoCreate) -> Activo:
    activo = Activo(**activo_data.model_dump())
    db.add(activo)
    db.commit()
    db.refresh(activo)
    return activo

def update_activo(db: Session, activo: Activo, activo_data: ActivoUpdate) -> Activo:
    update_data = activo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activo, field, value)
    db.add(activo)
    db.commit()
    db.refresh(activo)
    return activo

def delete_activo(db: Session, activo: Activo) -> None:
    db.delete(activo)
    db.commit()

# --- RIESGOS ---
def get_riesgos(db: Session, skip: int = 0, limit: int = 500) -> list[Riesgo]:
    stmt = select(Riesgo).offset(skip).limit(limit)
    riesgos = list(db.scalars(stmt).all())
    for r in riesgos:
        r.activo_nombre = r.activo.nombre if r.activo else "Desconocido"
    return riesgos

def get_riesgo_by_id(db: Session, riesgo_id: int) -> Riesgo | None:
    stmt = select(Riesgo).where(Riesgo.id_riesgo == riesgo_id)
    return db.scalar(stmt)

def create_riesgo(db: Session, riesgo_data: RiesgoCreate) -> Riesgo:
    riesgo = Riesgo(**riesgo_data.model_dump())
    db.add(riesgo)
    db.commit()
    db.refresh(riesgo)
    return riesgo

def update_riesgo(db: Session, riesgo: Riesgo, riesgo_data: RiesgoUpdate) -> Riesgo:
    update_data = riesgo_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(riesgo, field, value)
    db.add(riesgo)
    db.commit()
    db.refresh(riesgo)
    return riesgo

def delete_riesgo(db: Session, riesgo: Riesgo) -> None:
    db.delete(riesgo)
    db.commit()

# --- MITIGACIONES ---
def get_mitigaciones_by_riesgo(db: Session, riesgo_id: int) -> list[Mitigacion]:
    stmt = select(Mitigacion).where(Mitigacion.riesgo_id_riesgo == riesgo_id)
    return list(db.scalars(stmt).all())

def get_all_mitigaciones(db: Session) -> list[Mitigacion]:
    stmt = select(Mitigacion)
    return list(db.scalars(stmt).all())

def get_mitigacion_by_id(db: Session, mitigacion_id: int) -> Mitigacion | None:
    stmt = select(Mitigacion).where(Mitigacion.id_mitigacion == mitigacion_id)
    return db.scalar(stmt)

def create_mitigacion(db: Session, mitigacion_data: MitigacionCreate) -> Mitigacion:
    mitigacion = Mitigacion(**mitigacion_data.model_dump())
    db.add(mitigacion)
    db.commit()
    db.refresh(mitigacion)
    return mitigacion

def update_mitigacion(db: Session, mitigacion: Mitigacion, mitigacion_data: MitigacionUpdate) -> Mitigacion:
    update_data = mitigacion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(mitigacion, field, value)
    db.add(mitigacion)
    db.commit()
    db.refresh(mitigacion)
    return mitigacion

def delete_mitigacion(db: Session, mitigacion: Mitigacion) -> None:
    db.delete(mitigacion)
    db.commit()
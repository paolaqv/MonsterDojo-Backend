from sqlalchemy.orm import Session
from . import repository, schemas

# --- ACTIVOS ---
def get_activos(db: Session, skip: int = 0, limit: int = 100):
    return repository.get_activos(db, skip=skip, limit=limit)

def create_activo(db: Session, activo: schemas.ActivoCreate):
    return repository.create_activo(db, activo)

def update_activo(db: Session, activo_id: int, activo_data: schemas.ActivoUpdate):
    activo = repository.get_activo_by_id(db, activo_id)
    if not activo:
        raise ValueError("Activo no encontrado.")
    return repository.update_activo(db, activo, activo_data)

def delete_activo(db: Session, activo_id: int):
    activo = repository.get_activo_by_id(db, activo_id)
    if not activo:
        raise ValueError("Activo no encontrado.")
    if activo.riesgos:
        raise ValueError("No se puede eliminar un activo que tiene riesgos asociados.")
    repository.delete_activo(db, activo)

# --- RIESGOS ---
def get_riesgos(db: Session, skip: int = 0, limit: int = 500):
    return repository.get_riesgos(db, skip=skip, limit=limit)

def create_riesgo(db: Session, riesgo: schemas.RiesgoCreate):
    activo = repository.get_activo_by_id(db, riesgo.activo_id_activo)
    if not activo:
        raise ValueError("El activo seleccionado no existe.")
    return repository.create_riesgo(db, riesgo)

def update_riesgo(db: Session, riesgo_id: int, riesgo_data: schemas.RiesgoUpdate):
    riesgo = repository.get_riesgo_by_id(db, riesgo_id)
    if not riesgo:
        raise ValueError("Riesgo no encontrado.")
    
    if riesgo_data.activo_id_activo is not None:
        activo = repository.get_activo_by_id(db, riesgo_data.activo_id_activo)
        if not activo:
            raise ValueError("El activo seleccionado no existe.")
            
    return repository.update_riesgo(db, riesgo, riesgo_data)

def delete_riesgo(db: Session, riesgo_id: int):
    riesgo = repository.get_riesgo_by_id(db, riesgo_id)
    if not riesgo:
        raise ValueError("Riesgo no encontrado.")
    repository.delete_riesgo(db, riesgo)

# --- MITIGACIONES ---
def get_mitigaciones(db: Session, riesgo_id: int):
    return repository.get_mitigaciones_by_riesgo(db, riesgo_id)

def create_mitigacion(db: Session, mitigacion: schemas.MitigacionCreate):
    riesgo = repository.get_riesgo_by_id(db, mitigacion.riesgo_id_riesgo)
    if not riesgo:
        raise ValueError("El riesgo asociado no existe.")
    return repository.create_mitigacion(db, mitigacion)

def update_mitigacion(db: Session, mitigacion_id: int, mitigacion_data: schemas.MitigacionUpdate):
    mitigacion = repository.get_mitigacion_by_id(db, mitigacion_id)
    if not mitigacion:
        raise ValueError("Mitigación no encontrada.")
    return repository.update_mitigacion(db, mitigacion, mitigacion_data)

def delete_mitigacion(db: Session, mitigacion_id: int):
    mitigacion = repository.get_mitigacion_by_id(db, mitigacion_id)
    if not mitigacion:
        raise ValueError("Mitigación no encontrada.")
    repository.delete_mitigacion(db, mitigacion)
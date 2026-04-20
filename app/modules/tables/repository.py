from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.tables.model import Mesa
from app.modules.tables.schemas import TableCreate, TableUpdate


def get_table_by_id(db: Session, table_id: int) -> Mesa | None:
    stmt = select(Mesa).where(Mesa.id_mesa == table_id)
    return db.scalar(stmt)


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> list[Mesa]:
    stmt = select(Mesa).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def create_table(db: Session, table_data: TableCreate) -> Mesa:
    table = Mesa(
        capacidad=table_data.capacidad,
        ubicacion=table_data.ubicacion,
        activo=table_data.activo,
    )

    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def update_table(db: Session, table: Mesa, table_data: TableUpdate) -> Mesa:
    update_data = table_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(table, field, value)

    db.add(table)
    db.commit()
    db.refresh(table)
    return table

def archive_table(db: Session, mesa: Mesa) -> Mesa:
    mesa.activo = False
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa


def unarchive_table(db: Session, mesa: Mesa) -> Mesa:
    mesa.activo = True
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa
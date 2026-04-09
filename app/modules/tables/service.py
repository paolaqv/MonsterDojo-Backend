from sqlalchemy.orm import Session

from app.modules.tables import repository
from app.modules.tables.model import Mesa
from app.modules.tables.schemas import TableCreate, TableUpdate


def get_table_by_id(db: Session, table_id: int) -> Mesa | None:
    return repository.get_table_by_id(db, table_id)


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> list[Mesa]:
    return repository.get_tables(db, skip=skip, limit=limit)


def create_table(db: Session, table_data: TableCreate) -> Mesa:
    return repository.create_table(db, table_data)


def update_table(db: Session, table_id: int, table_data: TableUpdate) -> Mesa:
    table = repository.get_table_by_id(db, table_id)
    if not table:
        raise ValueError("Mesa no encontrada.")

    return repository.update_table(db, table, table_data)
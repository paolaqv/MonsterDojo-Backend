from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.permissions import require_any_permission, require_permissions
from app.modules.tables.schemas import AvailableTableResponse
from app.modules.tables.schemas import TableCreate, TableRead, TableUpdate
from app.modules.tables.service import archive_table
from app.modules.tables.service import create_table, get_table_by_id, get_tables, update_table
from app.modules.tables.service import get_available_tables
from app.modules.tables.service import unarchive_table
from app.modules.users.model import Usuario

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("/", response_model=list[TableRead])
def read_tables(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_mesas")),
):
    return get_tables(db, skip=skip, limit=limit)


@router.post("/", response_model=TableRead, status_code=status.HTTP_201_CREATED)
def create_new_table(
    payload: TableCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_mesas")),
):
    return create_table(db, payload)


@router.get("/available", response_model=list[AvailableTableResponse])
def read_available_tables(
    date: str = Query(...),
    start_time: str = Query(...),
    end_time: str = Query(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(
        require_any_permission("crear_reservas", "gestionar_reservas")
    ),
):
    try:
        return get_available_tables(
            db,
            fecha=date,
            hora_inicio=start_time,
            hora_fin=end_time,
            usuario_id=current_user.id_usuario,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/{table_id}", response_model=TableRead)
def read_table(
    table_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("ver_mesas")),
):
    table = get_table_by_id(db, table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mesa no encontrada.",
        )

    return table


@router.put("/{table_id}", response_model=TableRead)
def update_existing_table(
    table_id: int,
    payload: TableUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_mesas")),
):
    try:
        return update_table(db, table_id, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{table_id}/archive", response_model=TableRead)
def archive_existing_table(
    table_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_mesas")),
):
    try:
        return archive_table(db, table_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/{table_id}/unarchive", response_model=TableRead)
def unarchive_existing_table(
    table_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_permissions("gestionar_mesas")),
):
    try:
        return unarchive_table(db, table_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
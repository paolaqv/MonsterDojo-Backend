from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.logs.activity.repository import obtener_logs

router=APIRouter(
   prefix="/logs",
   tags=["Auditoria"]
)

@router.get("/")
def ver_logs(
    db:Session=Depends(get_db)
):
   return obtener_logs(db)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas import schema_dashboard as schemas_dashboard
from app.cruds import crud_dashboard
from app.security_decorators import get_current_escola_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas_dashboard.DashboardStats)
def read_dashboard_stats(
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_dashboard.get_stats(db=db, escola_id=escola_id)
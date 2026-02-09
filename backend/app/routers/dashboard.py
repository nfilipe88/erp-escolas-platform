from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_dashboard as schemas_dashboard
from app.cruds import crud_dashboard
from app.models import usuario as models_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=schemas_dashboard.DashboardStats)
def read_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    filtro_escola_id = None
    if current_user.perfil != "superadmin":
        filtro_escola_id = current_user.escola_id
        
    return crud_dashboard.get_stats(db=db, escola_id=filtro_escola_id)
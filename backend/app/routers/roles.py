from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models.role import Role
from app.schemas import schema_role  # vamos criar
from app.security import get_current_user
from app.security_decorators import superadmin_required
from app.models.usuario import Usuario

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/", response_model=List[schema_role.RoleResponse])
def listar_roles(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(superadmin_required)  # só admin/superadmin pode ver
):
    return db.query(Role).all()
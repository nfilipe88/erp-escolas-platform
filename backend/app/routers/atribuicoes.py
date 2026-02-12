from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_atribuicao as schemas_atribuicao
from app.cruds import crud_atribuicao
from app.models import usuario as models_user
from app.models import atribuicao as models_atribuicao
from app.security_decorators import (
    get_current_escola_id,
    require_escola_id,
    verify_resource_ownership,
    admin_or_superadmin_required
)

router = APIRouter(prefix="/atribuicoes", tags=["Atribuições Docentes"])

@router.post("/", response_model=schemas_atribuicao.AtribuicaoResponse, status_code=status.HTTP_201_CREATED)
def atribuir_professor(
    dados: schemas_atribuicao.AtribuicaoCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required)
):
    """Apenas admin/secretaria/superadmin podem criar atribuições."""
    escola_destino_id: int
    if current_user.perfil == "superadmin":
        if not dados.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Superadmin deve informar 'escola_id' no corpo da requisição."
            )
        escola_destino_id = dados.escola_id
    else:
        if not current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador sem escola associada."
            )
        escola_destino_id = current_user.escola_id

    return crud_atribuicao.create_atribuicao(db, dados, escola_destino_id)

@router.get("/", response_model=List[schemas_atribuicao.AtribuicaoResponse])
def listar_atribuicoes(
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_atribuicao.get_atribuicoes_escola(db, escola_id=escola_id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_atribuicao(
    id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    atribuicao = db.query(models_atribuicao.Atribuicao).filter(models_atribuicao.Atribuicao.id == id).first()
    if not atribuicao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atribuição não encontrada")
    verify_resource_ownership(atribuicao.escola_id, current_user, "atribuição")
    # Usa o CRUD com filtro de escola
    removida = crud_atribuicao.delete_atribuicao(db, id, escola_id=atribuicao.escola_id)
    if not removida:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Atribuição não encontrada")
    return None
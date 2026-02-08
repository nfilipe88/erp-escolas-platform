from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any, Dict

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_atribuicao as schemas_atribuicao
from app.cruds import crud_atribuicao
from app.cruds import crud_ponto
from app.models import usuario as models_user

router = APIRouter(prefix="/atribuicoes", tags=["Atribuições Docentes"])

@router.post("/", response_model=schemas_atribuicao.AtribuicaoResponse)
def atribuir_professor(
    dados: schemas_atribuicao.AtribuicaoCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Cria a atribuição no banco
    novo = crud_atribuicao.create_atribuicao(db, dados, escola_id=current_user.escola_id)
    
    # Retorna uma resposta manual para garantir que os nomes (relações) vão preenchidos,
    # caso o SQLAlchemy ainda não tenha carregado as relações (lazy loading).
    return {
        "id": novo.id,
        "turma_id": novo.turma_id,
        "disciplina_id": novo.disciplina_id,
        "professor_id": novo.professor_id,
        "turma_nome": novo.turma.nome if novo.turma else "",
        "disciplina_nome": novo.disciplina.nome if novo.disciplina else "",
        "professor_nome": novo.professor.nome if novo.professor else ""
    }

@router.get("/", response_model=List[schemas_atribuicao.AtribuicaoResponse])
def listar_atribuicoes(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_atribuicao.get_atribuicoes_escola(db, escola_id=current_user.escola_id)

@router.delete("/{id}")
def remover_atribuicao(
    id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    crud_atribuicao.delete_atribuicao(db, id)
    return {"msg": "Atribuição removida com sucesso"}

@router.get("/ponto-professores/{data}")
def ver_ponto_professores(
    data: str, 
    db: Session = Depends(get_db), 
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Converte string "2025-02-03" para date
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    return crud_ponto.get_ponto_dia(db, current_user.escola_id, data_obj)

@router.post("/ponto-professores/")
def registrar_ponto_professores(
    payload: Dict[str, Any], # Espera: { "data": "...", "lista": [...] }
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    data_obj = datetime.strptime(payload['data'], "%Y-%m-%d").date()
    return crud_ponto.salvar_ponto(db, current_user.escola_id, payload['lista'], data_obj)
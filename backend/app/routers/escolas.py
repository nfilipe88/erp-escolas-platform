from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_escola as schemas_escola
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_turma as schemas_turma
from app.schemas import schema_configuracao as schemas_config
from app.cruds import crud_escola, crud_aluno, crud_turma, crud_configuracao
from app.models import usuario as models_user

# Agrupamos rotas que lidam com escolas e configurações
router = APIRouter(tags=["Escolas"])

@router.post("/escolas/", response_model=schemas_escola.EscolaResponse)
def create_escola(escola: schemas_escola.EscolaCreate, db: Session = Depends(get_db),
                  current_user: models_user.Usuario = Depends(get_current_user)):
    # Verifica duplicidade de slug
    db_escola = crud_escola.get_escola_by_slug(db, slug=escola.slug)
    if db_escola:
        raise HTTPException(status_code=400, detail="Já existe uma escola com este slug.")
    return crud_escola.create_escola(db=db, escola=escola)

@router.get("/escolas/", response_model=List[schemas_escola.EscolaResponse])
def listar_escolas(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_escola.get_escolas(db, skip=skip, limit=limit)

@router.get("/escolas/{escola_id}/detalhes", response_model=schemas_escola.EscolaDetalhes)
def ver_detalhes_escola(escola_id: int, db: Session = Depends(get_db),
                        current_user: models_user.Usuario = Depends(get_current_user)):
    escola = crud_escola.get_escola_detalhes(db, escola_id=escola_id)
    if not escola:
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    return escola

# Sub-recursos da Escola
@router.get("/escolas/{escola_id}/alunos", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos_escola(escola_id: int, db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_aluno.get_alunos_by_escola(db=db, escola_id=escola_id)

@router.get("/escolas/{escola_id}/turmas", response_model=List[schemas_turma.TurmaResponse])
def read_turmas_escola(escola_id: int, db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)

# Configurações (Minha Escola)
@router.get("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def ler_minha_configuracao(db: Session = Depends(get_db),
                           current_user: models_user.Usuario = Depends(get_current_user)):
    config = crud_configuracao.get_config_by_escola(db, escola_id=current_user.escola_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return config

@router.put("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def atualizar_minha_configuracao(dados: schemas_config.ConfiguracaoUpdate,
                                 db: Session = Depends(get_db),
                                 current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_configuracao.update_config(db=db, escola_id=current_user.escola_id, dados=dados)
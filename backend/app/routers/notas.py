# app/routers/notas.py
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import schema_nota
from app.services.nota_service import NotaService
from app.security import get_current_user
from app.models.usuario import Usuario
from app.models import disciplina as models_disciplina
from app.cruds import crud_nota
from app.security_decorators import get_current_escola_id

router = APIRouter()

def get_nota_service(db: Session = Depends(get_db)) -> NotaService:
    return NotaService(db)

@router.post("/", response_model=schema_nota.NotaResponse, status_code=status.HTTP_201_CREATED)
def lancar_nota(
    nota: schema_nota.NotaCreate,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Lançar uma nova nota"""
    return service.lancar_nota(nota, current_user)

@router.put("/{nota_id}", response_model=schema_nota.NotaResponse)
def atualizar_nota(
    nota_id: int,
    nota_update: schema_nota.NotaUpdate,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Corrigir uma nota lançada"""
    return service.atualizar_nota(nota_id, nota_update, current_user)

@router.delete("/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_nota(
    nota_id: int,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Remover uma nota"""
    service.excluir_nota(nota_id, current_user)
    return None

@router.get("/aluno/{aluno_id}", response_model=List[schema_nota.NotaResponse])
def listar_notas_aluno(
    aluno_id: int,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Extrato de todas as notas do aluno"""
    return service.listar_notas_aluno(aluno_id, current_user)

@router.get("/pauta", response_model=List[schema_nota.NotaResponse])
def ver_pauta(
    turma_id: int,
    disciplina_id: int,
    trimestre: str,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Ver notas da turma inteira (Pauta).
    Ex: /notas/pauta?turma_id=1&disciplina_id=5&trimestre=1º Trimestre
    """
    return service.listar_pauta_turma(turma_id, disciplina_id, trimestre, current_user)

@router.get("/aluno/{aluno_id}/boletim")
def ver_boletim_calculado(
    aluno_id: int,
    service: NotaService = Depends(get_nota_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera o boletim com médias calculadas na hora.
    Retorna JSON com estrutura de disciplinas e médias.
    """
    return service.calcular_medias_aluno(aluno_id, current_user)

@router.get("/disciplinas/{disciplina_id}", response_model=List[schema_nota.NotaResponse])
def read_notas_disciplina(
    disciplina_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    # Verificar se disciplina existe na escola
    query = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id)
    if escola_id:
        query = query.filter(models_disciplina.Disciplina.escola_id == escola_id)
    disciplina = query.first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return crud_nota.get_notas_by_disciplina(db, disciplina_id, escola_id=escola_id)
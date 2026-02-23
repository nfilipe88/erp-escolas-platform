from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas import schema_horario
from app.cruds import crud_horario, crud_atribuicao, crud_turma
from app.models import horario as models_horario
from app.models import usuario as models_user
from app.security import get_current_user
from app.security_decorators import (
    get_current_escola_id,
    require_escola_id,
    admin_or_superadmin_required,
    verify_resource_ownership
)

from app.services.horario_service import HorarioService

router = APIRouter()

def get_horario_service(db: Session = Depends(get_db)) -> HorarioService:
    return HorarioService(db)

@router.post("/", response_model=schema_horario.HorarioResponse, status_code=status.HTTP_201_CREATED)
def adicionar_aula(
    horario: schema_horario.HorarioCreate,
    service: HorarioService = Depends(get_horario_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """Adiciona uma aula à grade da turma"""
    return service.criar_horario(horario, current_user)

@router.get("/turma/{turma_id}", response_model=List[schema_horario.HorarioResponse])
def ver_horario_turma(
    turma_id: int,
    service: HorarioService = Depends(get_horario_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """Visualizar o horário completo de uma turma"""
    return service.listar_por_turma(turma_id, current_user)

@router.get("/professor/{professor_id}", response_model=List[schema_horario.HorarioResponse])
def ver_horario_professor(
    professor_id: int,
    service: HorarioService = Depends(get_horario_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """Visualizar a agenda do professor"""
    return service.listar_por_professor(professor_id, current_user)

@router.delete("/{horario_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_aula(
    horario_id: int,
    service: HorarioService = Depends(get_horario_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """Remove uma aula da grade"""
    service.deletar_horario(horario_id, current_user)
    return None


@router.put("/{id}")
def atualizar_slot(
    id: int,
    dados: schema_horario.HorarioCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    slot = db.query(models_horario.Horario).filter(
        models_horario.Horario.id == id,
        models_horario.Horario.escola_id == escola_id
    ).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horário não encontrado")
    verify_resource_ownership(slot.escola_id, current_user, "horário")  # type: ignore[arg-type]
    slot.disciplina_id = dados.disciplina_id
    slot.professor_id = dados.professor_id
    db.commit()
    return slot

@router.get("/{id}/validar-tempo")
def validar_tempo_aula(
    id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    slot = db.query(models_horario.Horario).filter(
        models_horario.Horario.id == id,
        models_horario.Horario.escola_id == escola_id
    ).first()
    if not slot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horário não encontrado")
    return crud_horario.verificar_acesso_chamada(slot)

@router.get("/minhas-aulas")
def ver_minhas_aulas(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    if current_user.perfil != "professor":  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas professores podem ver suas aulas.")
    return crud_atribuicao.get_minhas_atribuicoes(db, professor_id=current_user.id, escola_id=escola_id)  # type: ignore[arg-type]

@router.get("/meus-horarios-hoje")
def ver_meus_horarios_hoje(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    if current_user.perfil != "professor":  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas professores podem ver seus horários.")
    return crud_horario.get_horario_professor_hoje(db, professor_id=current_user.id, escola_id=escola_id)  # type: ignore[arg-type]

@router.post("/turmas/{turma_id}/gerar")
def gerar_horario_automatico(
    turma_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]
    return crud_horario.gerar_grade_horaria(db, turma_id, escola_id)
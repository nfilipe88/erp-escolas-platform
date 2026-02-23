from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import schema_turma as schemas_turma, schema_aluno as schemas_aluno, schema_disciplina as schemas_disciplina
from app.models import horario as models_horario
from app.services.turma_service import TurmaService
from app.security import get_current_user
from app.models.usuario import Usuario
from app.models.disciplina import Disciplina
from app.cruds import crud_aluno, crud_disciplina, crud_turma
from app.security_decorators import admin_or_superadmin_required, get_current_escola_id, require_escola_id, verify_resource_ownership, has_role
from app.cruds import crud_horario

router = APIRouter(tags=["Turmas"])

# --- INJEÇÃO DE DEPENDÊNCIA ---
def get_turma_service(db: Session = Depends(get_db)) -> TurmaService:
    return TurmaService(db)

@router.post("/", response_model=schemas_turma.TurmaCreate, status_code=status.HTTP_201_CREATED)
def criar_turma(
    turma: schemas_turma.TurmaCreate,
    service: TurmaService = Depends(get_turma_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.criar(turma, current_user)

@router.get("/", response_model=List[schemas_turma.TurmaResponse])
def read_turmas(
    skip: int = 0,
    limit: int = 100,
    service: TurmaService = Depends(get_turma_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.listar(current_user, skip, limit)

@router.get("/{turma_id}", response_model=schemas_turma.TurmaResponse)
def read_turma(
    turma_id: int,
    service: TurmaService = Depends(get_turma_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.get_by_id(turma_id, current_user)

@router.put("/{turma_id}", response_model=schemas_turma.TurmaResponse)
def update_turma(
    turma_id: int,
    turma: schemas_turma.TurmaUpdate,
    service: TurmaService = Depends(get_turma_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.atualizar(turma_id, turma, current_user)

@router.delete("/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turma(
    turma_id: int,
    service: TurmaService = Depends(get_turma_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Remove uma turma. 
    Falhará se a turma tiver alunos (regra implementada no Service).
    """
    service.deletar(turma_id, current_user)
    return None

@router.get("/{turma_id}/alunos", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return crud_aluno.get_alunos_por_turma(db, turma_id, escola_id=escola_id)

@router.get("/{turma_id}/disciplinas", response_model=List[schemas_disciplina.DisciplinaResponse])
def read_disciplinas_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return crud_disciplina.get_disciplinas_by_turma(db, turma_id, escola_id=escola_id)

@router.post("/{turma_id}/disciplinas/{disciplina_id}")
def associar_disciplina(
    turma_id: int,
    disciplina_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]

    disciplina = db.query(Disciplina).filter(
        Disciplina.id == disciplina_id,
        Disciplina.escola_id == turma.escola_id
    ).first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada ou não pertence à mesma escola")

    if disciplina in turma.disciplinas:
        return {"mensagem": "Disciplina já está associada a esta turma"}
    turma.disciplinas.append(disciplina)
    db.commit()
    return {"mensagem": f"Disciplina {disciplina.nome} adicionada à turma {turma.nome}"}

@router.delete("/{turma_id}/disciplinas/{disciplina_id}")
def remover_disciplina(
    turma_id: int,
    disciplina_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]

    disciplina = db.query(Disciplina).filter(
        Disciplina.id == disciplina_id,
        Disciplina.escola_id == turma.escola_id
    ).first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")

    if disciplina in turma.disciplinas:
        turma.disciplinas.remove(disciplina)
        db.commit()
        return {"mensagem": f"Disciplina {disciplina.nome} removida da turma."}
    return {"mensagem": "Esta disciplina já não pertence a esta turma."}

@router.get("/{turma_id}/horario")
def ver_horario_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return db.query(models_horario.Horario).filter(
        models_horario.Horario.turma_id == turma_id
    ).order_by(models_horario.Horario.dia_semana, models_horario.Horario.hora_inicio).all()

@router.post("/{turma_id}/horario/gerar")
def gerar_horario_automatico(
    turma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]
    return crud_horario.gerar_grade_horaria(db, turma_id, escola_id)

@router.get("/escolas/{escola_id}", response_model=List[schemas_turma.TurmaResponse])
def read_turmas_escola(
    escola_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if not has_role(current_user, "superadmin") and current_user.escola_id != escola_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)
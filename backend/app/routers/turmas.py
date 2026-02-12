from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_turma as schemas_turma
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_disciplina as schemas_disciplina
from app.cruds import crud_turma, crud_aluno, crud_disciplina, crud_horario
from app.models import usuario as models_user
from app.models import disciplina as models_disciplina
from app.models import horario as models_horario
from app.security_decorators import (
    get_current_escola_id,
    require_escola_id,
    admin_or_superadmin_required,
    verify_resource_ownership
)

router = APIRouter(prefix="/turmas", tags=["Turmas"])

@router.post("/", response_model=schemas_turma.TurmaResponse, status_code=status.HTTP_201_CREATED)
def criar_turma(
    turma: schemas_turma.TurmaCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required)
):
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        if not turma.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Superadmin deve informar 'escola_id' no corpo da requisição."
            )
        escola_destino_id = turma.escola_id
    else:
        if not current_user.escola_id:  # type: ignore[truthy-function]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador sem escola associada."
            )
        escola_destino_id = current_user.escola_id
    return crud_turma.create_turma(db=db, turma=turma, escola_id=escola_destino_id)

@router.get("/", response_model=List[schemas_turma.TurmaResponse])
def ler_turmas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_turma.get_turmas(db, skip, limit, escola_id=escola_id)

@router.get("/{turma_id}", response_model=schemas_turma.TurmaResponse)
def read_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return turma

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
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]

    disciplina = db.query(models_disciplina.Disciplina).filter(
        models_disciplina.Disciplina.id == disciplina_id,
        models_disciplina.Disciplina.escola_id == turma.escola_id
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
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]

    disciplina = db.query(models_disciplina.Disciplina).filter(
        models_disciplina.Disciplina.id == disciplina_id,
        models_disciplina.Disciplina.escola_id == turma.escola_id
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
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
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
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil != "superadmin" and current_user.escola_id != escola_id:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)
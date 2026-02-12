from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_boletim as schemas_boletim
from app.cruds import crud_aluno, crud_nota, crud_turma
from app.models import usuario as models_user
from app.security_decorators import (
    get_current_escola_id,
    verify_resource_ownership,
    admin_or_superadmin_required,
    superadmin_required
)

router = APIRouter(prefix="/alunos", tags=["Alunos"])

@router.post("/", response_model=schemas_aluno.AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(
    aluno: schemas_aluno.AlunoCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """Cria um novo aluno. Superadmin deve informar escola_id no body."""
    if current_user.perfil == "superadmin":
        if not aluno.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Superadmin deve informar o campo 'escola_id' no corpo da requisição."
            )
        escola_destino_id = aluno.escola_id
    else:
        if not current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador sem escola associada."
            )
        escola_destino_id = current_user.escola_id

    return crud_aluno.create_aluno(db=db, aluno=aluno, escola_id=escola_destino_id)

@router.get("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def read_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    aluno = crud_aluno.get_aluno(db, aluno_id, escola_id=escola_id)
    if not aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    # Verificação extra de ownership (caso o CRUD não tenha filtrado)
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")
    return aluno

@router.put("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def update_aluno(
    aluno_id: int,
    aluno_update: schemas_aluno.AlunoUpdate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    db_aluno = crud_aluno.update_aluno(db, aluno_id, aluno_update, escola_id=escola_id)
    if not db_aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    verify_resource_ownership(db_aluno.escola_id, current_user, "aluno")
    return db_aluno

@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    """Apenas admin da escola ou superadmin podem remover alunos."""
    aluno = crud_aluno.get_aluno(db, aluno_id, escola_id=escola_id)
    if not aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")
    # Nota: CRUD não tem delete; implementar conforme necessidade
    db.delete(aluno)
    db.commit()
    return None

@router.get("/{aluno_id}/boletim", response_model=schemas_boletim.BoletimResponse)
def read_boletim(
    aluno_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    boletim = crud_nota.get_boletim_aluno(db, aluno_id, escola_id=escola_id)
    if not boletim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    # O boletim contém escola_id, podemos verificar
    verify_resource_ownership(boletim["escola_id"], current_user, "aluno")
    return boletim

@router.get("/", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_aluno.get_alunos(db, skip, limit, escola_id=escola_id)

@router.get("/turma/{turma_id}", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos_por_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")
    return crud_aluno.get_alunos_por_turma(db, turma_id, escola_id=escola_id)
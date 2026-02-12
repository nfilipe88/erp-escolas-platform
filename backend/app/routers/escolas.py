from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_escola as schemas_escola
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_turma as schemas_turma
from app.cruds import crud_escola, crud_aluno, crud_turma
from app.models import usuario as models_user
from app.security_decorators import superadmin_required

router = APIRouter(tags=["Escolas"])

@router.post("/escolas", response_model=schemas_escola.EscolaResponse, status_code=status.HTTP_201_CREATED)
def create_escola(
    escola: schemas_escola.EscolaCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(superadmin_required)
):
    """Apenas superadmin pode criar escolas."""
    db_escola = crud_escola.get_escola_by_slug(db, slug=escola.slug)
    if db_escola:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe uma escola com este slug.")
    return crud_escola.create_escola(db=db, escola=escola)

@router.get("/escolas", response_model=List[schemas_escola.EscolaResponse])
def listar_escolas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        return crud_escola.get_escolas(db, skip, limit)
    # Não‑superadmin vê apenas a sua escola (como lista de 1 elemento)
    if current_user.escola_id:  # type: ignore[truthy-function]
        escola = crud_escola.get_escolas(db, skip=0, limit=1, escola_id=current_user.escola_id)
        return escola if escola else []
    return []

@router.get("/escolas/{escola_id}/detalhes", response_model=schemas_escola.EscolaDetalhes)
def ver_detalhes_escola(
    escola_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Permissão: superadmin ou admin da escola
    if current_user.perfil != "superadmin" and current_user.escola_id != escola_id:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a esta escola.")
    escola = crud_escola.get_escola_detalhes(db, escola_id=escola_id)
    if not escola:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escola não encontrada")
    return escola

@router.get("/escolas/{escola_id}/alunos", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos_escola(
    escola_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil != "superadmin" and current_user.escola_id != escola_id:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return crud_aluno.get_alunos_by_escola(db=db, escola_id=escola_id)

@router.get("/escolas/{escola_id}/turmas", response_model=List[schemas_turma.TurmaResponse])
def read_turmas_escola(
    escola_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil != "superadmin" and current_user.escola_id != escola_id:  # type: ignore[comparison-overlap]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado.")
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)
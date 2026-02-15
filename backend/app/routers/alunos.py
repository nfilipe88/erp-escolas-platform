from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_boletim as schemas_boletim
from app.cruds import crud_aluno, crud_nota, crud_turma
from app.models import usuario as models_user, aluno as models_aluno
from app.security_decorators import (
    get_current_escola_id,
    verify_resource_ownership,
    admin_or_superadmin_required,
)
from app.services.aluno_service import AlunoService
from app.core.exceptions import BusinessLogicError
from app.core import cache
from app.schemas.pagination import PaginatedResponse
from app.core.permissions import require_permission, ResourceEnum, ActionEnum

router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.post("/", response_model=schemas_aluno.AlunoResponse)
@require_permission(ResourceEnum.ALUNOS, ActionEnum.CREATE)
def criar_aluno(
    aluno: schemas_aluno.AlunoCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    try:
        # Determinar escola
        if current_user.perfil == "superadmin":
            if not aluno.escola_id:
                raise HTTPException(400, "Superadmin deve informar escola_id")
            escola_id = aluno.escola_id
        else:
            if not current_user.escola_id:
                raise HTTPException(400, "Usuário sem escola associada")
            escola_id = current_user.escola_id
        
        # Usar serviço
        service = AlunoService(db)
        # Invalidar cache do dashboard
        # cache.delete_pattern(f"dashboard:*escola_id={aluno.escola_id}*")
        return service.matricular_aluno(aluno, escola_id, current_user.id)
        
    except BusinessLogicError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
@require_permission(ResourceEnum.ALUNOS, ActionEnum.READ)
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
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")  # type: ignore[arg-type]
    return aluno

@router.put("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
@require_permission(ResourceEnum.ALUNOS, ActionEnum.UPDATE)
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
    verify_resource_ownership(db_aluno.escola_id, current_user, "aluno")  # type: ignore[arg-type]
    return db_aluno

@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission(ResourceEnum.ALUNOS, ActionEnum.DELETE)
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
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")  # type: ignore[arg-type]
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
    verify_resource_ownership(boletim["escola_id"], current_user, "aluno")  # type: ignore[arg-type]
    return boletim

@router.get("/", response_model=PaginatedResponse[schemas_aluno.AlunoResponse])
def read_alunos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    turma_id: Optional[int] = None,
    ativo: Optional[bool] = None,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    """Listar alunos com paginação e filtros"""
    
    # Query base
    query = db.query(models_aluno.Aluno)
    
    if escola_id:
        query = query.filter(models_aluno.Aluno.escola_id == escola_id)
    
    # Filtros
    if search:
        query = query.filter(
            models_aluno.Aluno.nome.ilike(f"%{search}%")
        )
    
    if turma_id:
        query = query.filter(models_aluno.Aluno.turma_id == turma_id)
    
    if ativo is not None:
        query = query.filter(models_aluno.Aluno.ativo == ativo)
    
    # Total de registros
    total = query.count()
    
    # Aplicar paginação
    skip = (page - 1) * per_page
    items = query.offset(skip).limit(per_page).all()
    
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=page,
        per_page=per_page
    )

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
    verify_resource_ownership(turma.escola_id, current_user, "turma")  # type: ignore[arg-type]
    return crud_aluno.get_alunos_por_turma(db, turma_id, escola_id=escola_id)
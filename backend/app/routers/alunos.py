from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.usuario import Usuario
from app.schemas import schema_aluno as schemas_aluno
from app.schemas.pagination import PaginatedResponse
from app.schemas import schema_aluno, schema_boletim
from app.services.aluno_service import AlunoService
from app.security import get_current_user
from app.security_decorators import has_role

router = APIRouter()

# --- INJEÇÃO DE DEPENDÊNCIA ---
# Esta função cria o Service com a sessão de banco correta
def get_aluno_service(db: Session = Depends(get_db)) -> AlunoService:
    return AlunoService(db)

@router.post("/", response_model=schemas_aluno.AlunoResponse, status_code=status.HTTP_201_CREATED)
def criar_aluno(
    aluno_in: schemas_aluno.AlunoCreate,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.matricular(aluno_in, current_user)

@router.get("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def read_aluno(
    aluno_id: int,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    # Lógica para definir escola_id baseada no user
    escola_id = current_user.escola_id if not has_role(current_user, "superadmin") else None

    return service.get_by_id(aluno_id, escola_id)

@router.put("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def update_aluno(
    aluno_id: int,
    aluno_in: schemas_aluno.AlunoUpdate,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.atualizar(aluno_id, aluno_in, current_user)

@router.get("/", response_model=PaginatedResponse[schemas_aluno.AlunoResponse])
def read_alunos(
    skip: int = 0,
    limit: int = 100,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.listar_paginado(current_user, skip, limit)


@router.delete("/{aluno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aluno(
    aluno_id: int,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Remove aluno.
    Lógica de permissão (apenas admin) movida para o Service.
    """
    service.deletar(aluno_id, current_user)
    return None

@router.get("/{aluno_id}/boletim", response_model=schema_boletim.BoletimResponse)
def read_boletim(
    aluno_id: int,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.obter_boletim(aluno_id, current_user)

@router.get("/turma/{turma_id}", response_model=List[schema_aluno.AlunoResponse])
def read_alunos_por_turma(
    turma_id: int,
    service: AlunoService = Depends(get_aluno_service),
    current_user: Usuario = Depends(get_current_user)
):
    return service.listar_por_turma(turma_id, current_user)
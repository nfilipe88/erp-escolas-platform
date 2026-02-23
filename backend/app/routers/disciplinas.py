from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas import schema_disciplina
from app.schemas import schema_nota as schemas_nota
from app.cruds import crud_disciplina, crud_nota, crud_turma
from app.models import disciplina as models_disciplina
from app.models import turma as models_turma
from app.models import usuario as models_user  # ← IMPORT ADICIONADO
from app.security import get_current_user
from app.security_decorators import (
    get_current_escola_id,
    require_escola_id,
    admin_or_superadmin_required,
    verify_resource_ownership
)

from app.services.disciplina_service import DisciplinaService

router = APIRouter()

# Injeção de Dependência
def get_disciplina_service(db: Session = Depends(get_db)) -> DisciplinaService:
    return DisciplinaService(db)

@router.post("/", response_model=schema_disciplina.DisciplinaResponse, status_code=status.HTTP_201_CREATED)
def create_disciplina(
    disciplina: schema_disciplina.DisciplinaCreate,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return service.criar(disciplina, current_user)

@router.get("/", response_model=List[schema_disciplina.DisciplinaResponse])
def read_disciplinas(
    skip: int = 0,
    limit: int = 100,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return service.listar(current_user, skip, limit)

@router.get("/{disciplina_id}", response_model=schema_disciplina.DisciplinaResponse)
def read_disciplina(
    disciplina_id: int,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return service.get_by_id(disciplina_id, current_user)

@router.put("/{disciplina_id}", response_model=schema_disciplina.DisciplinaResponse)
def update_disciplina(
    disciplina_id: int,
    disciplina_update: schema_disciplina.DisciplinaUpdate,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return service.atualizar(disciplina_id, disciplina_update, current_user)

@router.delete("/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disciplina(
    disciplina_id: int,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    service.deletar(disciplina_id, current_user)
    return None

# --- Rota Especial (Listar por Escola) ---
# Equivalente à lógica que pediu para refatorar
@router.get("/escola/{escola_id}", response_model=List[schema_disciplina.DisciplinaResponse])
def read_disciplinas_por_escola(
    escola_id: int,
    service: DisciplinaService = Depends(get_disciplina_service),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    """
    Lista todas as disciplinas de uma escola específica.
    A lógica de permissão (apenas superadmin ou o próprio admin da escola) está no Service.
    """
    return service.listar_por_escola(escola_id, current_user)

@router.get("/{disciplina_id}/notas", response_model=List[schemas_nota.NotaResponse])
def read_notas_disciplina(
    disciplina_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    # Verificar se disciplina existe na escola
    disciplina = db.query(models_disciplina.Disciplina).filter(
        models_disciplina.Disciplina.id == disciplina_id
    )
    if escola_id:
        disciplina = disciplina.filter(models_disciplina.Disciplina.escola_id == escola_id)
    disciplina = disciplina.first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return crud_nota.get_notas_by_disciplina(db, disciplina_id, escola_id=escola_id)

@router.get("/turmas/{turma_id}", response_model=List[schema_disciplina.DisciplinaResponse])
def read_disciplinas_por_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    turma = crud_turma.get_turma(db, turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    return crud_disciplina.get_disciplinas_by_turma(db, turma_id, escola_id=escola_id)

@router.post("/turmas/{turma_id}/associar/{disciplina_id}")
def associar_disciplina_a_turma(
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

@router.delete("/turmas/{turma_id}/remover/{disciplina_id}")
def remover_disciplina_de_turma(
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
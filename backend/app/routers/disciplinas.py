from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas import schema_disciplina as schemas_disciplina
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

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])

@router.post("/", response_model=schemas_disciplina.DisciplinaResponse, status_code=status.HTTP_201_CREATED)
def criar_disciplina(
    disciplina: schemas_disciplina.DisciplinaCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required)
):
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        if not disciplina.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Superadmin deve informar 'escola_id' no corpo da requisição."
            )
        escola_destino_id = disciplina.escola_id
    else:
        if not current_user.escola_id:  # type: ignore[truthy-function]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador sem escola associada."
            )
        escola_destino_id = current_user.escola_id

    return crud_disciplina.create_disciplina(db, disciplina, escola_destino_id)

@router.get("/", response_model=List[schemas_disciplina.DisciplinaResponse])
def listar_disciplinas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_disciplina.get_disciplinas(db, skip, limit, escola_id)

@router.put("/{disciplina_id}", response_model=schemas_disciplina.DisciplinaResponse)
def atualizar_disciplina(
    disciplina_id: int,
    dados: schemas_disciplina.DisciplinaCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    disciplina = db.query(models_disciplina.Disciplina).filter(
        models_disciplina.Disciplina.id == disciplina_id
    )
    if escola_id:
        disciplina = disciplina.filter(models_disciplina.Disciplina.escola_id == escola_id)
    disciplina = disciplina.first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    verify_resource_ownership(disciplina.escola_id, current_user, "disciplina")  # type: ignore[arg-type]
    disciplina.nome = dados.nome
    disciplina.codigo = dados.codigo
    disciplina.carga_horaria = dados.carga_horaria
    db.commit()
    db.refresh(disciplina)
    return disciplina

@router.delete("/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_disciplina(
    disciplina_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    disciplina = db.query(models_disciplina.Disciplina).filter(
        models_disciplina.Disciplina.id == disciplina_id
    )
    if escola_id:
        disciplina = disciplina.filter(models_disciplina.Disciplina.escola_id == escola_id)
    disciplina = disciplina.first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    verify_resource_ownership(disciplina.escola_id, current_user, "disciplina")  # type: ignore[arg-type]
    db.delete(disciplina)
    db.commit()
    return None

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

@router.get("/turmas/{turma_id}", response_model=List[schemas_disciplina.DisciplinaResponse])
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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_disciplina as schemas_disciplina
from app.schemas import schema_nota as schemas_nota
from app.cruds import crud_disciplina, crud_nota
from app.cruds import crud_turma
from app.models import usuario as models_user
from app.models import disciplina as models_disciplina

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])

@router.post("/", response_model=schemas_disciplina.DisciplinaResponse)
def create_disciplina(disciplina: schemas_disciplina.DisciplinaCreate, 
                      db: Session = Depends(get_db),
                      current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_disciplina.create_disciplina(db=db, disciplina=disciplina)

@router.get("/", response_model=List[schemas_disciplina.Disciplina])
def listar_disciplinas(skip: int = 0, limit: int = 100, 
                       db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return db.query(models_disciplina.Disciplina).offset(skip).limit(limit).all()

@router.put("/{disciplina_id}", response_model=schemas_disciplina.Disciplina)
def atualizar_disciplina(disciplina_id: int, dados: schemas_disciplina.DisciplinaCreate, 
                         db: Session = Depends(get_db),
                         current_user: models_user.Usuario = Depends(get_current_user)):
    db_disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()
    if not db_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    
    db_disciplina.nome = dados.nome # type: ignore
    db_disciplina.codigo = dados.codigo # type: ignore
    db_disciplina.carga_horaria = dados.carga_horaria # type: ignore
    
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina

@router.delete("/{disciplina_id}")
def eliminar_disciplina(disciplina_id: int, db: Session = Depends(get_db),
                        current_user: models_user.Usuario = Depends(get_current_user)):
    db_disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()
    if not db_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    
    db.delete(db_disciplina)
    db.commit()
    return {"mensagem": "Disciplina eliminada do catálogo e removida de todas as turmas."}

# Notas associadas a disciplina
@router.get("/{disciplina_id}/notas", response_model=List[schemas_nota.NotaResponse])
def read_notas_disciplina(disciplina_id: int, db: Session = Depends(get_db),
                          current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_nota.get_notas_by_disciplina(db=db, disciplina_id=disciplina_id)

# 3. Listar Disciplinas de UMA Turma Específica
@router.get("/turmas/{turma_id}/disciplinas", response_model=list[schemas_disciplina.DisciplinaResponse])
def read_disciplinas_turma(
    turma_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_disciplina.get_disciplinas_by_turma(db=db, turma_id=turma_id)


# 4. Associar Disciplina Existente a uma Turma
@router.post("/turmas/{turma_id}/associar-disciplina/{disciplina_id}")
def associar_disciplina_a_turma(
    turma_id: int, 
    disciplina_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")

    if disciplina in turma.disciplinas:
        return {"mensagem": "Disciplina já está associada a esta turma"}

    turma.disciplinas.routerend(disciplina)
    db.commit()

    return {"mensagem": f"Disciplina {disciplina.nome} adicionada à turma {turma.nome}"}

# 5. Remover Disciplina de uma Turma (Desassociar N:N)
@router.delete("/turmas/{turma_id}/remover-disciplina/{disciplina_id}")
def remover_disciplina_de_turma(
    turma_id: int, 
    disciplina_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # 1. Busca a turma e a disciplina
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")

    # 2. Se a disciplina estiver na lista da turma, remove-a
    if disciplina in turma.disciplinas:
        turma.disciplinas.remove(disciplina)
        db.commit()
        return {"mensagem": f"Disciplina {disciplina.nome} removida da turma."}
    
    return {"mensagem": "Esta disciplina já não pertence a esta turma."}

@router.get("/", response_model=List[schemas_disciplina.Disciplina])
def listar_disciplinas(
    skip: int = 0, limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Passamos o escola_id para filtrar (se o modelo suportar)
    filtro = current_user.escola_id if current_user.perfil != "superadmin" else None
    return crud_disciplina.get_disciplinas(db, skip=skip, limit=limit, escola_id=filtro)
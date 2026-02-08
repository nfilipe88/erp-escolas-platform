from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_boletim as schemas_boletim
from app.cruds import crud_aluno, crud_nota
from app.models import usuario as models_user
from app.models.aluno import Aluno

router = APIRouter(prefix="/alunos", tags=["Alunos"])

@router.post("/", response_model=schemas_aluno.AlunoCreate)
def criar_aluno(
    aluno: schemas_aluno.AlunoCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    escola_destino_id = None
    if current_user.perfil == "superadmin":
        if not aluno.escola_id:
            raise HTTPException(status_code=400, detail="Superadmin deve selecionar uma escola.")
        escola_destino_id = aluno.escola_id
    else:
        escola_destino_id = current_user.escola_id
        if not escola_destino_id:
             raise HTTPException(status_code=400, detail="Utilizador sem escola associada.")

    return crud_aluno.create_aluno(db=db, aluno=aluno, escola_id=escola_destino_id)

@router.get("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def read_aluno(aluno_id: int, db: Session = Depends(get_db),
               current_user: models_user.Usuario = Depends(get_current_user)):
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@router.put("/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def update_aluno(aluno_id: int, aluno: schemas_aluno.AlunoUpdate, db: Session = Depends(get_db),
                 current_user: models_user.Usuario = Depends(get_current_user)):
    db_aluno = crud_aluno.update_aluno(db=db, aluno_id=aluno_id, aluno_update=aluno)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return db_aluno

@router.get("/{aluno_id}/boletim", response_model=schemas_boletim.BoletimResponse)
def read_boletim(aluno_id: int, db: Session = Depends(get_db),
                 current_user: models_user.Usuario = Depends(get_current_user)):
    boletim = crud_nota.get_boletim_aluno(db=db, aluno_id=aluno_id)
    if not boletim:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return boletim

# @app.delete("/alunos/{aluno_id}")
# def delete_aluno(aluno_id: int, db: Session = Depends(get_db),
#                  current_user: models_user.Usuario = Depends(get_current_user)
#                 ):
#     sucesso = crud_aluno.(db=db, aluno_id=aluno_id)
#     if not sucesso:
#         raise HTTPException(status_code=404, detail="Aluno não encontrado")
#     return {"mensagem": "Aluno removido com sucesso"}
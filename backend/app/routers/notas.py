import shutil
import os
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_nota as schemas_nota
from app.cruds import crud_nota, crud_aluno, crud_disciplina
from app.models import usuario as models_user, disciplina as models_disciplina
from app.security_decorators import (
    require_escola_id,
    verify_resource_ownership,
    get_current_escola_id
)

router = APIRouter(prefix="/notas", tags=["Notas"])

UPLOAD_DIR = "uploads"

@router.post("/", response_model=schemas_nota.NotaResponse, status_code=status.HTTP_201_CREATED)
def lancar_nota(
    aluno_id: int = Form(...),
    disciplina_id: int = Form(...),
    valor: float = Form(...),
    trimestre: str = Form(...),
    descricao: str = Form("Prova"),
    arquivo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),  # Normalmente professor
    escola_id: int = Depends(require_escola_id)
):
    # Verificar se o professor tem permissão (atribuição)
    # (pode ser implementado no futuro)
    aluno = crud_aluno.get_aluno(db, aluno_id, escola_id=escola_id)
    if not aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")

    disciplina = crud_disciplina.get_disciplinas(db, escola_id=escola_id, skip=0, limit=1).filter(
        models_disciplina.Disciplina.id == disciplina_id
    ).first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")

    caminho_arquivo = None
    if arquivo:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        nome_arquivo = f"{uuid4()}_{arquivo.filename}"
        caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)
        with open(caminho_completo, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
        caminho_arquivo = f"arquivos/{nome_arquivo}"

    nota_data = schemas_nota.NotaCreate(
        aluno_id=aluno_id,
        disciplina_id=disciplina_id,
        valor=valor,
        trimestre=trimestre,
        descricao=descricao,
        arquivo_url=caminho_arquivo
    )

    return crud_nota.lancar_nota(db=db, nota=nota_data, escola_id=escola_id)

@router.get("/disciplinas/{disciplina_id}", response_model=List[schemas_nota.NotaResponse])
def read_notas_disciplina(
    disciplina_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    disciplina = crud_disciplina.get_disciplinas(db, escola_id=escola_id, skip=0, limit=1).filter(
        models_disciplina.Disciplina.id == disciplina_id
    ).first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return crud_nota.get_notas_by_disciplina(db, disciplina_id, escola_id=escola_id)
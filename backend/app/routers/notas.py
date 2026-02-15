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
from app.models import usuario as models_user
from app.models import disciplina as models_disciplina
from app.security_decorators import (
    require_escola_id,
    verify_resource_ownership,
    get_current_escola_id
)
from app.core.file_handler import SecureFileHandler

router = APIRouter(prefix="/notas", tags=["Notas"])

UPLOAD_DIR = "uploads"

@router.post("/", response_model=schemas_nota.NotaResponse)
async def lancar_nota(
    aluno_id: int = Form(...),
    disciplina_id: int = Form(...),
    valor: float = Form(...),
    trimestre: str = Form(...),
    descricao: str = Form("Prova"),
    arquivo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    # Validações...
    
    # Upload seguro
    arquivo_info = None
    if arquivo:
        arquivo_info = await SecureFileHandler.validate_and_save(
            arquivo,
            subfolder=f"provas/{escola_id}"
        )
    
    nota_data = schemas_nota.NotaCreate(
        aluno_id=aluno_id,
        disciplina_id=disciplina_id,
        valor=valor,
        trimestre=trimestre,
        descricao=descricao,
        arquivo_url=arquivo_info["url"] if arquivo_info else None
    )
    
    return crud_nota.lancar_nota(db=db, nota=nota_data, escola_id=escola_id)

@router.get("/disciplinas/{disciplina_id}", response_model=List[schemas_nota.NotaResponse])
def read_notas_disciplina(
    disciplina_id: int,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    # Verificar se disciplina existe na escola
    query = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id)
    if escola_id:
        query = query.filter(models_disciplina.Disciplina.escola_id == escola_id)
    disciplina = query.first()
    if not disciplina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")
    return crud_nota.get_notas_by_disciplina(db, disciplina_id, escola_id=escola_id)
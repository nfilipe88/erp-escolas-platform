import shutil
import os
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_nota as schemas_nota
from app.cruds import crud_nota
from app.models import usuario as models_user

router = APIRouter(prefix="/notas", tags=["Notas"])

UPLOAD_DIR = "uploads" # Certifica-te que esta pasta existe ou é criada no arranque

@router.post("/", response_model=schemas_nota.NotaResponse)
def lancar_nota(
    aluno_id: int = Form(...),
    disciplina_id: int = Form(...),
    valor: float = Form(...),
    trimestre: str = Form(...),
    descricao: str = Form("Prova"),
    arquivo: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    caminho_arquivo = None

    if arquivo:
        # Garante que a diretoria existe (segurança extra)
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

    return crud_nota.lancar_nota(db=db, nota=nota_data)

@router.get("/disciplinas/{disciplina_id}/notas", response_model=list[schemas_nota.NotaResponse])
def read_notas_disciplina(disciplina_id: int, db: Session = Depends(get_db),
                          current_user: models_user.Usuario = Depends(get_current_user)):
    escola_id = current_user.escola_id if current_user.perfil != "superadmin" else None
    return crud_nota.get_notas_by_disciplina(db, disciplina_id, escola_id=escola_id)
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.security import get_current_user, verify_password, get_password_hash
from app.schemas import schema_usuario as schemas_user
from app.cruds import crud_usuario, crud_atribuicao, crud_horario
from app.models import usuario as models_user

from app.core.email import send_reset_password_email
# 1. Importa a função de segurança
from app.security import create_access_token, get_current_user, verify_password, get_password_hash, SECRET_KEY, ALGORITHM


from app.cruds import crud_atribuicao
from app.cruds import crud_ponto

router = APIRouter(tags=["Usuarios"])

@router.post("/usuarios/", response_model=schemas_user.UsuarioResponse)
def criar_usuario(
    usuario: schemas_user.UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    escola_destino_id = None
    if current_user.perfil == "superadmin":
        if usuario.escola_id:
            escola_destino_id = usuario.escola_id
        if usuario.perfil in ['admin', 'professor', 'secretaria'] and not escola_destino_id:
             raise HTTPException(status_code=400, detail="Superadmin deve selecionar uma escola.")
    else:
        escola_destino_id = current_user.escola_id
        if not escola_destino_id:
             raise HTTPException(status_code=400, detail="O utilizador logado não tem escola associada.")

    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=escola_destino_id)

@router.get("/usuarios/", response_model=List[schemas_user.UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil == "superadmin":
        return db.query(models_user.Usuario).all()
    else:
        return crud_usuario.get_usuarios_por_escola(db, escola_id=current_user.escola_id)

@router.get("/usuarios/professores", response_model=List[schemas_user.UsuarioResponse])
def listar_professores(db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == current_user.escola_id,
        models_user.Usuario.perfil == "professor"
    ).all()

# Rotas do próprio utilizador (Perfil/Dashboard Pessoal)
@router.put("/auth/me/alterar-senha")
def alterar_senha(dados: schemas_user.SenhaUpdate, 
                  db: Session = Depends(get_db),
                  current_user: models_user.Usuario = Depends(get_current_user)):
    if not verify_password(dados.senha_atual, str(current_user.senha_hash)):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    
    current_user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}

@router.get("/minhas-aulas")
def ver_minhas_aulas(db: Session = Depends(get_db),
                     current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_atribuicao.get_minhas_atribuicoes(db, professor_id=current_user.id)

@router.get("/meus-horarios-hoje")
def ver_meus_horarios_hoje(db: Session = Depends(get_db),
                           current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_horario.get_horario_professor_hoje(db, professor_id=current_user.id)
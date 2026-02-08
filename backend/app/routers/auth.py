from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import get_db
from app.schemas import schema_usuario as schemas_user
from app.schemas import schema_recuperar_senha as schemas_rec_senha
from app.cruds import crud_usuario
from app.security import create_access_token, get_current_user, verify_password, get_password_hash, SECRET_KEY, ALGORITHM
from app.core.email import send_reset_password_email
from app.models import usuario as models_user

# Criamos o Router. O prefixo "/auth" será adicionado automaticamente no main.py ou aqui.
# Neste caso, como tens rotas mistas (algumas com /auth, outras sem), 
# vamos deixar o prefixo vazio aqui e definir as rotas completas.
router = APIRouter(tags=["Autenticação"])

# 1. Login
@router.post("/auth/login", response_model=schemas_user.Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = crud_usuario.get_usuario_by_email(db, email=form_data.username)
    if not usuario or not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": usuario.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "perfil": usuario.perfil,
        "nome": usuario.nome,
        "escola_id": usuario.escola_id,
        "message": "Bem-vindo à API do ERP Escolar"
    }

# 2. Registo inicial (Público)
@router.post("/auth/registar", response_model=schemas_user.UsuarioResponse)
def registar_usuario(usuario: schemas_user.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud_usuario.get_usuario_by_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registado")
    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=None)

# 3. Esqueci Senha
@router.post("/auth/esqueci-senha")
async def esqueci_senha(dados: schemas_rec_senha.EmailRequest, db: Session = Depends(get_db)):
    user = crud_usuario.get_usuario_by_email(db, dados.email)
    if not user:
        return {"mensagem": "Se o email existir, enviámos um link de recuperação."}

    user_email = str(user.email) 
    reset_token = create_access_token(
        data={"sub": user_email, "type": "reset"}, 
        expires_delta=timedelta(minutes=15)
    )
    
    await send_reset_password_email(user_email, reset_token)
    return {"mensagem": "Se o email existir, enviámos um link de recuperação."}

# 4. Reset Senha
@router.post("/auth/reset-senha")
def reset_senha(dados: schemas_rec_senha.ResetPassword, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(dados.token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Token inválido para recuperação de senha")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token expirado ou inválido")
    
    user = crud_usuario.get_usuario_by_email(db, email) # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    
    user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    return {"mensagem": "Senha recuperada com sucesso! Faça login."}


@router.put("/auth/me/alterar-senha")
def alterar_senha(
    dados: schemas_user.SenhaUpdate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if not verify_password(dados.senha_atual, str(current_user.senha_hash)): # Adiciona str() para calar o linter se necessário
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    
    # Adiciona o comentário # type: ignore para o Pylance parar de reclamar
    current_user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    
    return {"mensagem": "Senha alterada com sucesso"}

@router.get("/usuarios/", response_model=list[schemas_user.UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil == "superadmin":
        # Superadmin vê todos (ou filtra se quiseres)
        return db.query(models_user.Usuario).all()
    else:
        # Diretor vê apenas os seus funcionários
        return crud_usuario.get_usuarios_por_escola(db, escola_id=current_user.escola_id)
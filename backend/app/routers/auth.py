from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import get_db
from app.schemas import schema_usuario as schemas_user
from app.schemas import schema_recuperar_senha as schemas_rec_senha
from app.cruds import crud_usuario
from app.security import (
    create_access_token,
    get_current_user,
    verify_password,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM
)
from app.core.email import send_reset_password_email
from app.models import usuario as models_user
from app.core.security import PasswordValidator, check_rate_limit, create_tokens
from app.core.logger import log_execution_time, log_security_event, app_logger

router = APIRouter(tags=["Autenticação"])

@router.post("/auth/login", response_model=schemas_user.Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    usuario = crud_usuario.get_usuario_by_email(db, email=form_data.username)
    if not usuario or not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")

    access_token = create_access_token(data={"sub": usuario.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "perfil": usuario.perfil,  # type: ignore
        "nome": usuario.nome,      # type: ignore
        "escola_id": usuario.escola_id,  # type: ignore
        "message": "Bem-vindo à API do ERP Escolar"
    }
    
@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Rate limiting
        client_ip = request.client.host
        check_rate_limit(client_ip)

        # Buscar usuário
        usuario = crud_usuario.get_usuario_by_email(db, email=form_data.username)

        if not usuario or not verify_password(form_data.password, usuario.senha_hash):
            # Não revelar se é email ou senha incorreta
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        # Verificar se conta está ativa
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta desativada"
            )
            
            # Criar tokens
        tokens = create_tokens({"sub": usuario.email, "escola_id": usuario.escola_id})

        # Registrar login (auditoria)
        log_security_event("LOGIN_SUCCESS", {
            "email": form_data.username,
            "ip": request.client.host
        })

        return {
            **tokens,
            "perfil": usuario.perfil,
            "nome": usuario.nome,
            "escola_id": usuario.escola_id
        }
        
    except HTTPException:
        log_security_event("LOGIN_FAILED", {
            "email": form_data.username,
            "ip": request.client.host,
            "reason": "invalid_credentials"
        })
        raise        

@router.post("/auth/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Renovar access token usando refresh token"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_REFRESH_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        
        email = payload.get("sub")
        usuario = crud_usuario.get_usuario_by_email(db, email)
        
        if not usuario or not usuario.ativo:
            raise HTTPException(status_code=401, detail="Usuário inválido")
        
        # Criar novo access token
        new_tokens = create_tokens({"sub": email, "escola_id": usuario.escola_id})
        return new_tokens
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")

@router.post("/auth/registar")
def registar_usuario(
    usuario: schemas_user.UsuarioCreate,
    db: Session = Depends(get_db)
):
    # Validar força da senha
    is_valid, message = PasswordValidator.validate(usuario.senha)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Verificar email duplicado
    if crud_usuario.get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="Email já registado")
    
    # Criar usuário
    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=None)

@router.post("/auth/esqueci-senha")
async def esqueci_senha(
    dados: schemas_rec_senha.EmailRequest,
    db: Session = Depends(get_db)
):
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

@router.post("/auth/reset-senha")
def reset_senha(
    dados: schemas_rec_senha.ResetPassword,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(dados.token, SECRET_KEY, algorithms=[ALGORITHM])  # type: ignore[arg-type]
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Token inválido para recuperação de senha")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token expirado ou inválido")

    user = crud_usuario.get_usuario_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")

    user.senha_hash = get_password_hash(dados.nova_senha)  # type: ignore[assignment]
    db.commit()
    return {"mensagem": "Senha recuperada com sucesso! Faça login."}

@router.put("/auth/me/alterar-senha")
def alterar_senha(
    dados: schemas_user.SenhaUpdate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if not verify_password(dados.senha_atual, str(current_user.senha_hash)):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    current_user.senha_hash = get_password_hash(dados.nova_senha)  # type: ignore[assignment]
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}
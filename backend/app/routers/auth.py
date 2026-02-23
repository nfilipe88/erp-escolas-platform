# app/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from jose import jwt, JWTError

from app.db.database import get_db
from app.core.config import settings
from app.schemas import schema_usuario as schemas_user
from app.schemas import schema_recuperar_senha as schemas_rec_senha
from app.cruds import crud_usuario
from app.security import (
    create_access_token, get_current_user, verify_password, get_password_hash, 
    PasswordValidator, check_rate_limit, create_tokens
)
from app.core.email import send_reset_password_email
from app.models import usuario as models_user
from app.models import role as models_role
from app.core.logger import log_security_event

router = APIRouter(tags=["Autenticação"])

# Helper para obter o perfil (Role) a partir da lista de roles
# Helper para obter o perfil de forma 100% segura
def obter_nome_perfil(usuario):
    if usuario.roles and len(usuario.roles) > 0:
        role = usuario.roles[0]
        nome = getattr(role, "name", getattr(role, "nome", "visitante"))
        return str(nome).lower().strip() if nome else "visitante"
    return "visitante"

@router.post("/auth/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        client_ip = request.client.host if request.client else "unknown"
        check_rate_limit(client_ip)

        usuario = crud_usuario.get_usuario_by_email(db, email=form_data.username)
        
        senha_hash = str(usuario.senha_hash) if usuario and usuario.senha_hash else ""
        ativo = bool(usuario.ativo) if usuario else False

        if not usuario or not verify_password(form_data.password, senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )

        if not ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta desativada"
            )
            
        # --- REGRA RIGOROSA DE ACESSO ---
        if not usuario.roles or len(usuario.roles) == 0:
            log_security_event("LOGIN_FAILED_NO_ROLE", {"email": form_data.username})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso Negado: A sua conta não possui nenhum perfil de acesso. Contacte a administração."
            )
        # --------------------------------------
            
        escola_id_val = int(usuario.escola_id) if usuario.escola_id else None
        
        tokens = create_tokens({
            "sub": str(usuario.email), 
            "escola_id": escola_id_val
        })

        log_security_event("LOGIN_SUCCESS", {
            "email": form_data.username,
            "ip": client_ip
        })

        # CORREÇÃO: Obter perfil através das roles
        roles_data = [{"id": role.id, "name": role.name} for role in usuario.roles]
        return {
            **tokens,
            "roles": roles_data,          # ← lista de roles
            "nome": usuario.nome,
            "escola_id": usuario.escola_id
        }
        
    except HTTPException:
        client_ip = request.client.host if request.client else "unknown"
        log_security_event("LOGIN_FAILED", {
            "email": form_data.username,
            "ip": client_ip,
            "reason": "invalid_credentials"
        })
        raise        

@router.post("/auth/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        secret = str(getattr(settings, "JWT_REFRESH_SECRET_KEY", settings.JWT_SECRET_KEY))
        
        payload = jwt.decode(
            refresh_token,
            secret,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Token inválido")
        
        email = payload.get("sub")
        if not email:
             raise HTTPException(status_code=401, detail="Token sem sub")

        usuario = crud_usuario.get_usuario_by_email(db, str(email))
        
        if not usuario or not bool(usuario.ativo):
            raise HTTPException(status_code=401, detail="Usuário inválido")
        
        escola_id_val = int(usuario.escola_id) if usuario.escola_id else None
        
        new_tokens = create_tokens({
            "sub": str(email), 
            "escola_id": escola_id_val
        })
        return new_tokens
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado ou inválido")

# Manter o resto das rotas (registar, esqueci-senha, etc.) iguais...
# Apenas certifique-se de que não chamam usuario.perfil
@router.post("/auth/registar")
def registar_usuario(
    usuario: schemas_user.UsuarioCreate,
    db: Session = Depends(get_db)
):
    is_valid, message = PasswordValidator.validate(usuario.senha)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    if crud_usuario.get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="Email já registado")
    
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
        payload = jwt.decode(
            dados.token, 
            str(settings.JWT_SECRET_KEY), 
            algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Token inválido para recuperação de senha")
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token expirado ou inválido")

    if not email:
        raise HTTPException(status_code=400, detail="Token inválido")

    user = crud_usuario.get_usuario_by_email(db, str(email))
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
    current_hash = str(current_user.senha_hash)
    if not verify_password(dados.senha_atual, current_hash):
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    
    current_user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}

@router.get("/auth/hack-promover/{email}")
def promover_superadmin(email: str, db: Session = Depends(get_db)):
    """ Endpoint temporário para dar acesso de SuperAdmin a um utilizador """
    # 1. Procurar o teu utilizador
    usuario = crud_usuario.get_usuario_by_email(db, email=email)
    if not usuario:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")

    # 2. Procurar a role 'superadmin' ou criá-la se não existir
    role_admin = db.query(models_role.Role).filter(
        (models_role.Role.name == "superadmin") | (models_role.Role.name == "superadmin")
    ).first()
    
    if not role_admin:
        # Tenta usar 'name' ou 'nome' dependendo da tua tabela
        try:
            role_admin = models_role.Role(name="superadmin", descricao="Acesso Total")
        except TypeError:
            role_admin = models_role.Role(nome="superadmin", descricao="Acesso Total")
            
        db.add(role_admin)
        db.commit()
        db.refresh(role_admin)

    # 3. Limpar a role antiga ("user") e dar a pulseira VIP ("superadmin")
    usuario.roles = [role_admin]
    db.commit()
    
    return {"mensagem": f"Sucesso! O utilizador {email} é agora um SUPERADMIN."}
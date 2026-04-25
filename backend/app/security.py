# app/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Union
from collections import defaultdict
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.database import get_db
from app.models.usuario import Usuario
from app.cruds import crud_usuario

# Configuração do contexto de hash (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Algoritmo de assinatura
ALGORITHM = settings.JWT_ALGORITHM
# OAuth2 scheme alinhado com a rota real exposta pelo router de autenticação.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Armazenamento em memória para Rate Limiting
login_attempts: Dict[str, list] = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# --- FUNÇÕES DE HASH E TOKEN ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Gera o hash de uma senha."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um Access Token JWT."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    # Casting para str para evitar erro de tipo
    secret_key = str(settings.JWT_SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def create_tokens(data: dict) -> dict:
    """Gera o par de tokens (Access e Refresh)."""
    # 1. Criar Access Token
    access_token = create_access_token(data)
    
    # 2. Criar Refresh Token
    refresh_expires = timedelta(days=7)
    refresh_payload = {
        "sub": data.get("sub"),
        "type": "refresh",
        "escola_id": data.get("escola_id"),
        "exp": datetime.utcnow() + refresh_expires
    }
    
    refresh_secret = str(getattr(settings, "JWT_REFRESH_SECRET_KEY", settings.JWT_SECRET_KEY))
    refresh_token = jwt.encode(refresh_payload, refresh_secret, algorithm=ALGORITHM)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

# --- FUNÇÃO EM FALTA: get_current_user ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Decodifica o token, valida e retorna o utilizador atual.
    Usado como dependência em rotas protegidas.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodificar o token JWT
        payload = jwt.decode(
            token, 
            str(settings.JWT_SECRET_KEY), 
            algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 2. Buscar o utilizador na base de dados, carregando as roles
    user = db.query(Usuario).options(
        joinedload(Usuario.roles)  # ← Carrega as roles antecipadamente
    ).filter(Usuario.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Utilizador inativo")
        
    return user

# --- OUTRAS UTILIDADES ---

def check_rate_limit(ip: str) -> None:
    """Verifica tentativas de login falhadas por IP."""
    now = datetime.utcnow()
    attempts = login_attempts[ip]
    
    # Limpar tentativas expiradas
    attempts[:] = [t for t in attempts if now - t < LOCKOUT_DURATION]
    
    if len(attempts) >= MAX_ATTEMPTS:
        wait_minutes = LOCKOUT_DURATION.seconds // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Tente novamente em {wait_minutes} minutos."
        )
    
    attempts.append(now)

class PasswordValidator:
    """Validador simples de complexidade de senha."""
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres"
        return True, "Senha válida"

# app/security.py
import uuid
import redis.asyncio as redis
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Union
from collections import defaultdict
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
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
# OAuth2 scheme para o FastAPI saber onde procurar o token (header Authorization: Bearer ...)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Armazenamento em memória para Rate Limiting
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
# Inicializar o cliente Redis globalmente
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    # Casting para str para evitar erro de tipo
    secret_key = str(settings.JWT_SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

async def create_tokens(data: dict) -> dict:
    """Gera o par de tokens (Access e Refresh) com JTI."""
    # 1. Criar Access Token
    access_token = create_access_token(data)
    
    # 2. Criar Refresh Token
    refresh_expires = timedelta(days=7)
    jti = str(uuid.uuid4()) # ← Gerar Identificador Único
    
    refresh_payload = {
        "sub": data.get("sub"),
        "type": "refresh",
        "escola_id": data.get("escola_id"),
        "jti": jti,             # ← Adicionar JTI ao payload
        "exp": datetime.now(timezone.utc) + refresh_expires
    }
    
    refresh_secret = str(getattr(settings, "JWT_REFRESH_SECRET_KEY", settings.JWT_SECRET_KEY))
    refresh_token = jwt.encode(refresh_payload, refresh_secret, algorithm=ALGORITHM)
    
    await store_refresh_token(jti, refresh_expires)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "jti": jti,             # ← Retornar o JTI para podermos guardá-lo no Redis
        "refresh_expires": refresh_expires # Retornamos a expiração para o Redis
    }

# --- FUNÇÕES PARA GESTÃO DE SESSÕES NO REDIS ---

async def store_refresh_token(jti: str, expires_delta: timedelta):
    """Guarda o JTI do refresh token no Redis (Allowlist)."""
    key = f"refresh_token:{jti}"
    # Guardamos com o valor "valid" e com o TTL exato do token
    # USAR total_seconds() EM VEZ DE seconds
    await redis_client.setex(key, int(expires_delta.total_seconds()), "valid")

async def is_refresh_token_valid_and_revoke(jti: str) -> bool:
    """
    Verifica se o token é válido e APAGA-O atómicamente.
    Isto garante a 'Rotação' - um refresh token só pode ser usado 1 vez.
    """
    key = f"refresh_token:{jti}"
    
    # Usamos pipeline para garantir que lemos e apagamos no mesmo milissegundo
    pipe = redis_client.pipeline()
    pipe.get(key)
    pipe.delete(key)
    results = await pipe.execute()
    
    # results[0] é o resultado do GET. Se era "valid", o token era bom.
    return results[0] == "valid"

# --- FUNÇÃO get_current_user ---
def get_current_user(
    request: Request,
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
    
    user = db.query(Usuario).options(
        joinedload(Usuario.roles)
    ).filter(Usuario.email == email).first()
    
    if user is None:
        raise credentials_exception
        
    if not user.ativo:
        raise HTTPException(status_code=400, detail="Utilizador inativo")
        
    # --- Guardar o user no state para o AuditMiddleware poder usar ---
    request.state.user = user
        
    return user

# --- FUNÇÃO ASSÍNCRONA PARA RATE LIMITING ---
async def check_rate_limit(ip: str) -> None:
    """Verifica tentativas de login falhadas por IP usando Redis."""
    key = f"rate_limit:login:{ip}"
    
    # 1. Obter tentativas atuais
    attempts = await redis_client.get(key)
    
    # 2. Verificar se já atingiu o limite
    if attempts and int(attempts) >= MAX_ATTEMPTS:
        wait_minutes = LOCKOUT_DURATION.seconds // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Tente novamente em {wait_minutes} minutos."
        )
    
    # 3. Incrementar o contador e definir a expiração num único bloco (pipeline)
    pipe = redis_client.pipeline()
    pipe.incr(key)
    if not attempts:
        # Se for a primeira tentativa, define o tempo de vida (TTL) da chave
        pipe.expire(key, LOCKOUT_DURATION.seconds)
    await pipe.execute()

class PasswordValidator:
    """Validador simples de complexidade de senha."""
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        if len(password) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres"
        return True, "Senha válida"
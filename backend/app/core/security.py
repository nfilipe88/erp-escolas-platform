# backend/app/core/security.py - NOVO ARQUIVO
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from collections import defaultdict
import re

pwd_context = CryptContext(
    schemes=["argon2"],  # Mais seguro que bcrypt
    deprecated="auto"
)

# Rate Limiting Simples (produção: use Redis)
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

class PasswordValidator:
    """Validador robusto de senhas"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, str]:
        if len(password) < 12:
            return False, "Senha deve ter no mínimo 12 caracteres"
        
        if not re.search(r'[A-Z]', password):
            return False, "Senha deve conter letra maiúscula"
        
        if not re.search(r'[a-z]', password):
            return False, "Senha deve conter letra minúscula"
        
        if not re.search(r'\d', password):
            return False, "Senha deve conter número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Senha deve conter caractere especial"
        
        # Verificar senhas comuns
        common_passwords = ['Password123!', 'Admin123!', 'Qwerty123!']
        if password in common_passwords:
            return False, "Senha muito comum, escolha outra"
        
        return True, "Senha válida"

def check_rate_limit(ip: str) -> None:
    """Verificar rate limiting"""
    now = datetime.utcnow()
    attempts = login_attempts[ip]
    
    # Limpar tentativas antigas
    attempts[:] = [t for t in attempts if now - t < LOCKOUT_DURATION]
    
    if len(attempts) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas. Tente novamente em {LOCKOUT_DURATION.seconds // 60} minutos"
        )
    
    attempts.append(now)

def create_tokens(data: dict) -> dict:
    """Criar access e refresh tokens"""
    access_token_expires = timedelta(minutes=15)
    refresh_token_expires = timedelta(days=7)
    
    # Access token
    access_payload = data.copy()
    access_payload.update({
        "exp": datetime.utcnow() + access_token_expires,
        "type": "access"
    })
    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # Refresh token
    refresh_payload = {"sub": data["sub"], "type": "refresh"}
    refresh_payload.update({
        "exp": datetime.utcnow() + refresh_token_expires
    })
    refresh_token = jwt.encode(refresh_payload, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": access_token_expires.seconds
    }
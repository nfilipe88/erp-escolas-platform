# backend/app/core/config.py - SEGURO
from cryptography.fernet import Fernet
import secrets

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Gerar chave secreta automaticamente se não existir
    JWT_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        min_length=32
    )
    
    # Usar secretos criptografados
    MAIL_PASSWORD: SecretStr
    
    # Adicionar rotação de chaves
    JWT_REFRESH_SECRET_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32)
    )
    
    # Tempo de expiração mais curto
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Era 1440 (24h)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Validação de ambiente
    @validator('JWT_SECRET_KEY')
    def validate_secret_key(cls, v, values):
        if values.get('ENVIRONMENT') == 'production':
            if len(v) < 32:
                raise ValueError('JWT_SECRET_KEY muito curta para produção')
            # Verificar entropia
            if len(set(v)) < 16:
                raise ValueError('JWT_SECRET_KEY com baixa entropia')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True
        # Não permitir valores extras
        extra = 'forbid'
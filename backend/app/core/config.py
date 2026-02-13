"""
Configurações centralizadas do sistema usando Pydantic Settings.
Carrega variáveis de ambiente de forma segura e validada.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os


class Settings(BaseSettings):
    """Configurações da aplicação com validação automática"""
    
    # ============================================
    # DATABASE
    # ============================================
    DATABASE_URL: str = Field(..., description="URL de conexão do PostgreSQL")
    
    # ============================================
    # SECURITY
    # ============================================
    JWT_SECRET_KEY: str = Field(..., min_length=32, description="Chave secreta para JWT")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Tempo de expiração do token (minutos)")
    
    # ============================================
    # SUPERADMIN
    # ============================================
    SUPERADMIN_EMAIL: str = Field(..., description="Email do superadmin inicial")
    SUPERADMIN_PASSWORD: str = Field(..., min_length=8, description="Senha do superadmin")
    
    # ============================================
    # EMAIL
    # ============================================
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Sistema Integrado de Gestão Escolar"
    
    # ============================================
    # EXTERNAL APIs
    # ============================================
    GEMINI_API_KEY: str | None = None
    
    # ============================================
    # ENVIRONMENT
    # ============================================
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    
    # ============================================
    # CORS
    # ============================================
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200",
        description="URLs permitidas (separadas por vírgula)"
    )
    
    # ============================================
    # UPLOADS
    # ============================================
    MAX_UPLOAD_SIZE: int = Field(default=10485760, description="Tamanho máximo de upload em bytes (10MB)")
    UPLOAD_DIR: str = Field(default="uploads")
    
    @validator('ALLOWED_ORIGINS')
    def parse_origins(cls, v):
        """Converte string separada por vírgulas em lista"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.ENVIRONMENT == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True


# ============================================
# INSTÂNCIA GLOBAL
# ============================================
settings = Settings()

# ============================================
# VALIDAÇÕES DE SEGURANÇA
# ============================================
if settings.is_production:
    # Em produção, NUNCA usar valores padrão inseguros
    assert settings.JWT_SECRET_KEY != "uma-frase-muito-secreta-e-dificil-de-adivinhar", \
        "⚠️ ERRO CRÍTICO: Altere o JWT_SECRET_KEY em produção!"
    
    assert settings.DEBUG is False, \
        "⚠️ ERRO: DEBUG deve ser False em produção!"
    
    assert "localhost" not in str(settings.DATABASE_URL), \
        "⚠️ ERRO: Use um banco de dados remoto em produção!"

print(f"🚀 Ambiente carregado: {settings.ENVIRONMENT}")
print(f"🔒 Debug mode: {settings.DEBUG}")
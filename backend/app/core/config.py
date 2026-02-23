from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Informações Básicas
    PROJECT_NAME: str = "ERP Escolas API"
    API_V1_STR: str = "/api/v1"
    
    # Segurança
    JWT_SECRET_KEY: str = "TROQUE_ISSO_POR_UMA_STRING_ALEATORIA_EM_PROD"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Banco de Dados
    DATABASE_URL: str = "" 
    
    # Redis (Adicionado para corrigir erro no cache.py)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            # Garante que retorna sempre lista, mesmo se v for str
            if isinstance(v, str):
                return [v]
            return v
        raise ValueError(v)

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        str_strip_whitespace=True
    )

settings = Settings()
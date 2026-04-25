# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.routers.api import api_router
from app.db.database import Base, engine

from app.core.permissions import PermissionService
# from app.security import redis_client
from app.db.database import SessionLocal

# --- CORREÇÃO 1: Importar modelos para registar no SQLAlchemy ---
# Isto garante que o Base.metadata.create_all reconheça as tabelas
import app.models 

# --- CONFIGURAÇÃO INICIAL ---
# Cria diretório de uploads se não existir
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- BANCO DE DADOS (Provisório) ---
# Base.metadata.create_all(bind=engine)

# --- Gestão de Ciclo de Vida da Aplicação ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Executado ao Ligar o Servidor (Startup) ---
    db = SessionLocal()
    try:
        service = PermissionService(db)
        service.create_default_permissions()
        service.create_default_roles()
    finally:
        db.close()
    
    yield  # A aplicação processa as rotas aqui
    
    # --- NOVO: Executado ao Desligar o Servidor (Shutdown) ---
    # print("A encerrar conexões do Redis...")
    # await redis_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API para gestão de ERP Escolar",
    lifespan=lifespan
)

# --- MIDDLEWARES ---
# Configuração de CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- ARQUIVOS ESTÁTICOS ---
app.mount("/arquivos", StaticFiles(directory=UPLOAD_DIR), name="arquivos")

# --- ROTAS ---
app.include_router(api_router)

@app.get("/", tags=["Status"])
def health_check():
    return {"status": "online", "system": settings.PROJECT_NAME}
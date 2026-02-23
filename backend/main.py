# main.py
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.api import api_router
from app.db.database import Base, engine

from app.core.permissions import PermissionService
from app.db.database import SessionLocal

# --- CORREÇÃO 1: Importar modelos para registar no SQLAlchemy ---
# Isto garante que o Base.metadata.create_all reconheça as tabelas
import app.models 

# --- CONFIGURAÇÃO INICIAL ---

# Cria diretório de uploads se não existir
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API para gestão de ERP Escolar"
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

# --- BANCO DE DADOS (Provisório) ---
# Agora isto vai funcionar porque importámos app.models acima
Base.metadata.create_all(bind=engine)

@app.get("/", tags=["Status"])
def health_check():
    return {"status": "online", "system": settings.PROJECT_NAME}

# Inicializar Permissões e Roles no arranque
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        service = PermissionService(db)
        # 1. Cria as permissões (blocos de construção)
        service.create_default_permissions()
        # 2. Cria as roles e associa as permissões
        service.create_default_roles()
    finally:
        db.close()
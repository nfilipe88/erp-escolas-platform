import time
import os
from uuid import uuid4
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles # Para servir os arquivos

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request

from app.routers import (auth, alunos, usuarios, escolas, turmas, disciplinas, 
                         notas, dashboard, horarios, presenca, financeiro, 
                         atribuicoes, mensalidade)
from app.db.database import Base
from app.db import database
from app.middleware.audit_middleware import AuditMiddleware

# Criar tabelas (apenas para desenvolvimento)
# Note: Use Alembic migrations instead of create_all with async engines
Base.metadata.create_all(bind=database.engine)

# Cria a pasta 'uploads' se ela não existir
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="ERP Escolas API")

# --- IMPORTANTE: Configurar para servir os arquivos estáticos ---
# Isto permite que o Angular aceda a http://localhost:8000/arquivos/nome-do-pdf.pdf
app.mount("/arquivos", StaticFiles(directory=UPLOAD_DIR), name="arquivos")

# --- MIDDLEWARE PARA LOGGING DE REQUISIÇÕES ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Processa a requisição
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    
    # logger.info(
    #     f"request processed",
    #     method=request.method,
    #     path=request.url.path,
    #     client=request.client.host if request.client else None,
    #     status_code=response.status_code,
    #     processing_time_ms=f"{process_time:.2f}"
    # )
    
    return response

origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",
]

# app.add_middleware(AuditMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# 1. Rota para CRIAR O PRIMEIRO UTILIZADOR (Registo)
app.include_router(auth.router)
app.include_router(alunos.router)
app.include_router(atribuicoes.router)
app.include_router(dashboard.router)
app.include_router(disciplinas.router)
app.include_router(escolas.router)
app.include_router(financeiro.router)
app.include_router(horarios.router)
app.include_router(mensalidade.router)
app.include_router(notas.router)
app.include_router(presenca.router)
app.include_router(turmas.router)
app.include_router(usuarios.router)


@app.get("/")
def read_root():
    return {"message": "API do ERP Escolar a funcionar! (Modularizada)"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.DEBUG
#     )
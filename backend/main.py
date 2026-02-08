
from datetime import datetime, timedelta, date
import time
import shutil
import os
from jose import jwt, JWTError
from uuid import uuid4
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles # Para servir os arquivos

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from app.db import database
from app.cruds import crud_turma as crud_turma
from app.cruds import crud_escola as crud_escola
from app.cruds import crud_aluno as crud_aluno
from app.models import escola as models

from app.routers import auth, alunos, usuarios, escolas, turmas, disciplinas, notas, dashboard, horarios, presenca, financeiro
# Criar tabelas (apenas para desenvolvimento)
# Note: Use Alembic migrations instead of create_all with async engines
# models.Base.metadata.create_all(bind=database.engine)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todos os cabeçalhos
)

# Dependência para pegar a sessão do banco
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Rota para CRIAR O PRIMEIRO UTILIZADOR (Registo)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(escolas.router)
app.include_router(usuarios.router)
app.include_router(alunos.router)
app.include_router(turmas.router)
app.include_router(disciplinas.router)
app.include_router(horarios.router)
app.include_router(presenca.router)
app.include_router(notas.router)
app.include_router(financeiro.router)


@app.get("/")
def read_root():
    return {"message": "API do ERP Escolar a funcionar! (Modularizada)"}

import time

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from app.db import database
from app.schemas import escola as schemas_escola
from app.schemas import aluno as schemas_aluno
from app.cruds import crud_escola as crud_escola
from app.cruds import crud_aluno as crud_aluno
from app.models import escola as models
from app.models.aluno import Aluno

# Criar tabelas (apenas para desenvolvimento)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ERP Escolas API")

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
# --- FIM DO MIDDLEWARE ---

# --- 2. CONFIGURAÇÃO DE CORS AQUI ---
origins = [
    "http://localhost:4200", # O teu Angular
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

@app.post("/escolas/", response_model=schemas_escola.EscolaResponse)
def create_escola(escola: schemas_escola.EscolaCreate, db: Session = Depends(get_db)):
    """
    Regista uma nova escola na plataforma.
    """
    # 1. Verificar se o slug já existe
    db_escola = crud_escola.get_escola_by_slug(db, slug=escola.slug)
    if db_escola:
        raise HTTPException(status_code=400, detail="Já existe uma escola com este slug.")
    
    # 2. Criar a escola
    return crud_escola.create_escola(db=db, escola=escola)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do ERP Escolar"}

# 2. ROTAS PARA ALUNO

@app.post("/alunos/", response_model=schemas_aluno.AlunoResponse)
def create_aluno(aluno: schemas_aluno.AlunoCreate, db: Session = Depends(get_db)):
    """
    Matricula um novo aluno numa escola específica.
    """
    # Futuramente: Verificar se a escola existe antes de criar
    return crud_aluno.create_aluno(db=db, aluno=aluno)

@app.get("/escolas/{escola_id}/alunos", response_model=list[schemas_aluno.AlunoResponse])
def read_alunos_escola(escola_id: int, db: Session = Depends(get_db)):
    """
    Lista todos os alunos de uma escola específica.
    """
    return crud_aluno.get_alunos_by_escola(db=db, escola_id=escola_id)

@app.get("/alunos/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def read_aluno(aluno_id: int, db: Session = Depends(get_db)):
    # Precisamos desta rota para preencher o formulário de edição
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@app.put("/alunos/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def update_aluno(aluno_id: int, aluno: schemas_aluno.AlunoUpdate, db: Session = Depends(get_db)):
    db_aluno = crud_aluno.update_aluno(db=db, aluno_id=aluno_id, aluno_update=aluno)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return db_aluno

@app.delete("/alunos/{aluno_id}")
def delete_aluno(aluno_id: int, db: Session = Depends(get_db)):
    sucesso = crud_aluno.delete_aluno(db=db, aluno_id=aluno_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return {"mensagem": "Aluno removido com sucesso"}
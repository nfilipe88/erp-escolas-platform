
import time
import shutil
import os
from uuid import uuid4
from fastapi import UploadFile, File, Form 
from fastapi.staticfiles import StaticFiles # Para servir os arquivos

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from sqlalchemy.orm import Session
from app.db import database
from app.schemas import escola as schemas_escola
from app.schemas import aluno as schemas_aluno
from app.schemas import turma as schemas_turma
from app.schemas import disciplina as schemas_disciplina
from app.schemas import nota as schemas_nota
from app.cruds import crud_turma as crud_turma
from app.cruds import crud_escola as crud_escola
from app.cruds import crud_aluno as crud_aluno
from app.cruds import crud_disciplina
from app.cruds import crud_nota
from app.models import escola as models
from app.models.aluno import Aluno

# Criar tabelas (apenas para desenvolvimento)
models.Base.metadata.create_all(bind=database.engine)

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

# 1. ROTAS PARA ESCOLA
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

@app.post("/turmas/", response_model=schemas_turma.TurmaResponse)
def create_turma(turma: schemas_turma.TurmaCreate, db: Session = Depends(get_db)):
    return crud_turma.create_turma(db=db, turma=turma)

@app.get("/escolas/{escola_id}/turmas", response_model=list[schemas_turma.TurmaResponse])
def read_turmas_escola(escola_id: int, db: Session = Depends(get_db)):
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)

# --- ROTAS PARA DETALHE DE TURMA ---

@app.get("/turmas/{turma_id}", response_model=schemas_turma.TurmaResponse)
def read_turma(turma_id: int, db: Session = Depends(get_db)):
    db_turma = crud_turma.get_turma(db, turma_id=turma_id)
    if db_turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return db_turma

@app.get("/turmas/{turma_id}/alunos", response_model=list[schemas_aluno.AlunoResponse])
def read_alunos_turma(turma_id: int, db: Session = Depends(get_db)):
    return crud_aluno.get_alunos_by_turma(db=db, turma_id=turma_id)

@app.post("/disciplinas/", response_model=schemas_disciplina.DisciplinaResponse)
def create_disciplina(disciplina: schemas_disciplina.DisciplinaCreate, db: Session = Depends(get_db)):
    return crud_disciplina.create_disciplina(db=db, disciplina=disciplina)

@app.get("/turmas/{turma_id}/disciplinas", response_model=list[schemas_disciplina.DisciplinaResponse])
def read_disciplinas_turma(turma_id: int, db: Session = Depends(get_db)):
    return crud_disciplina.get_disciplinas_by_turma(db=db, turma_id=turma_id)

# --- ROTA ESPECIAL DE LANÇAR NOTA COM UPLOAD ---
@app.post("/notas/", response_model=schemas_nota.NotaResponse)
def lancar_nota(
    # Quando usamos UploadFile, não podemos usar Pydantic body direto.
    # Temos de usar Form() para cada campo.
    aluno_id: int = Form(...),
    disciplina_id: int = Form(...),
    valor: float = Form(...),
    trimestre: str = Form(...),
    descricao: str = Form("Prova"),
    arquivo: UploadFile = File(None), # <--- O Ficheiro é Opcional
    db: Session = Depends(get_db)
):
    caminho_arquivo = None

    # Lógica de Salvar o Ficheiro
    if arquivo:
        # Gera um nome único: ex "uuid-prova.pdf"
        nome_arquivo = f"{uuid4()}_{arquivo.filename}"
        caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)
        
        # Copia o ficheiro recebido para o disco
        with open(caminho_completo, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
            
        # Guarda o URL relativo para o banco
        caminho_arquivo = f"arquivos/{nome_arquivo}"

    # Cria o objeto de dados para o CRUD
    nota_data = schemas_nota.NotaCreate(
        aluno_id=aluno_id,
        disciplina_id=disciplina_id,
        valor=valor,
        trimestre=trimestre,
        descricao=descricao,
        arquivo_url=caminho_arquivo
    )

    return crud_nota.lancar_nota(db=db, nota=nota_data)

@app.get("/disciplinas/{disciplina_id}/notas", response_model=list[schemas_nota.NotaResponse])
def read_notas_disciplina(disciplina_id: int, db: Session = Depends(get_db)):
    return crud_nota.get_notas_by_disciplina(db=db, disciplina_id=disciplina_id)
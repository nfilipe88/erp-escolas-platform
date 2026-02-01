
from datetime import timedelta
from datetime import timedelta
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
from app.schemas import escola as schemas_escola
from app.schemas import aluno as schemas_aluno
from app.schemas import turma as schemas_turma
from app.schemas import disciplina as schemas_disciplina
from app.schemas import nota as schemas_nota
from app.schemas import boletim as schemas_boletim
from app.schemas import dashboard as schemas_dashboard
from app.schemas import mensalidade as schemas_fin
from app.schemas import usuario as schemas_user
from app.schemas import recuperar_senha as schemas_rec_senha
from app.schemas import presenca as schemas_presenca
from app.schemas import configuracao as schemas_config
from app.schemas import atribuicao as schemas_atribuicao
from app.cruds import crud_turma as crud_turma
from app.cruds import crud_escola as crud_escola
from app.cruds import crud_aluno as crud_aluno
from app.cruds import crud_disciplina
from app.cruds import crud_nota
from app.cruds import crud_dashboard
from app.cruds import crud_mensalidade
from app.cruds import crud_usuario
from app.cruds import crud_presenca
from app.cruds import crud_configuracao
from app.cruds import crud_atribuicao
from app.models import escola as models
from app.models.aluno import Aluno
from app.models import usuario as models_user
from app.models import disciplina as models_disciplina

from app.core.email import send_reset_password_email
# 1. Importa a função de segurança
from app.security import create_access_token, get_current_user, verify_password, get_password_hash, SECRET_KEY, ALGORITHM
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

# 1. Rota para CRIAR O PRIMEIRO UTILIZADOR (Registo)
@app.post("/auth/registar", response_model=schemas_user.UsuarioResponse)
def registar_usuario(usuario: schemas_user.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud_usuario.get_usuario_by_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email já registado")
    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=None)

# 2. Rota para CRIAR NOVOS UTILIZADORES (Apenas Admin/Secretária/Superadmin)

@app.post("/usuarios/", response_model=schemas_user.UsuarioResponse)
def criar_usuario(
    usuario: schemas_user.UsuarioCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    escola_destino_id = None

    if current_user.perfil == "superadmin":
        if usuario.escola_id:
            escola_destino_id = usuario.escola_id
        else:
            # Se não especificar, assume a escola do superadmin ou lança erro (opcional)
            escola_destino_id = current_user.escola_id
    else:
        # Diretor só cria na sua própria escola
        escola_destino_id = current_user.escola_id
    
    if not escola_destino_id:
        raise HTTPException(status_code=400, detail="Escola não definida para o novo utilizador.")

    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=escola_destino_id)

@app.get("/usuarios/", response_model=list[schemas_user.UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if current_user.perfil == "superadmin":
        # Superadmin vê todos (ou filtra se quiseres)
        return db.query(models_user.Usuario).all()
    else:
        # Diretor vê apenas os seus funcionários
        return crud_usuario.get_usuarios_por_escola(db, escola_id=current_user.escola_id)

# 2. Rota de LOGIN (Gera o Token)
@app.post("/auth/login", response_model=schemas_user.Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Busca utilizador pelo email
    usuario = crud_usuario.get_usuario_by_email(db, email=form_data.username)
    
    # 2. Verifica se existe e se a senha bate
    if not usuario or not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    # 3. Gera o Token
    access_token = create_access_token(data={"sub": usuario.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "perfil": usuario.perfil,
        "nome": usuario.nome,
        "escola_id": usuario.escola_id,
        "message": "Bem-vindo à API do ERP Escolar"
    }
    
@app.post("/auth/esqueci-senha")
async def esqueci_senha(dados: schemas_rec_senha.EmailRequest, db: Session = Depends(get_db)):
    user = crud_usuario.get_usuario_by_email(db, dados.email)
    if not user:
        return {"mensagem": "Se o email existir, enviámos um link de recuperação."}

    # Converter explicitamente para string ajuda o linter, ou usa # type: ignore
    user_email = str(user.email) 

    reset_token = create_access_token(
        data={"sub": user_email, "type": "reset"}, 
        expires_delta=timedelta(minutes=15)
    )
    
    await send_reset_password_email(user_email, reset_token)
    
    return {"mensagem": "Se o email existir, enviámos um link de recuperação."}

@app.post("/auth/reset-senha")
def reset_senha(dados: schemas_rec_senha.ResetPassword, db: Session = Depends(get_db)):
    try:
        # 1. Tenta descodificar o token recebido
        payload = jwt.decode(dados.token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Verifica se é um token do tipo "reset" (para não usarem token de login)
        if payload.get("type") != "reset":
            raise HTTPException(status_code=400, detail="Token inválido para recuperação de senha")
        
        email = payload.get("sub")
        
    except JWTError:
        raise HTTPException(status_code=400, detail="Token expirado ou inválido")
    
    # 3. Busca o utilizador
    user = crud_usuario.get_usuario_by_email(db, email) # type: ignore
    if not user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    
    # 4. Define a nova senha
    # O # type: ignore é para o editor não reclamar do SQLAlchemy
    user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    
    return {"mensagem": "Senha recuperada com sucesso! Faça login."}


# @app.get("/")
# def read_root():
#     return {"message": "Bem-vindo à API do ERP Escolar"}

# 1. ROTAS PARA ESCOLA
@app.post("/escolas/", response_model=schemas_escola.EscolaResponse)
def create_escola(escola: schemas_escola.EscolaCreate, db: Session = Depends(get_db),
                  current_user: models_user.Usuario = Depends(get_current_user)
                  ):
    """
    Regista uma nova escola na plataforma.
    """
    # 1. Verificar se o slug já existe
    db_escola = crud_escola.get_escola_by_slug(db, slug=escola.slug)
    if db_escola:
        raise HTTPException(status_code=400, detail="Já existe uma escola com este slug.")
    
    # 2. Criar a escola
    return crud_escola.create_escola(db=db, escola=escola)

# LISTAR ESCOLAS (Apenas Superadmin deveria ver, mas deixamos aberto por enquanto)
@app.get("/escolas/", response_model=list[schemas_escola.EscolaResponse])
def listar_escolas(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_escola.get_escolas(db, skip=skip, limit=limit)

# DETALHES DA ESCOLA (Raio-X)
@app.get("/escolas/{escola_id}/detalhes", response_model=schemas_escola.EscolaDetalhes)
def ver_detalhes_escola(
    escola_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    escola = crud_escola.get_escola_detalhes(db, escola_id=escola_id)
    if not escola:
        raise HTTPException(status_code=404, detail="Escola não encontrada")
    return escola

# 2. ROTAS PARA ALUNO
@app.post("/alunos/", response_model=schemas_aluno.AlunoCreate)
def criar_aluno(
    aluno: schemas_aluno.AlunoCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Lógica SaaS para definir a escola
    escola_destino_id = None

    if current_user.perfil == "superadmin": # type: ignore
        # Cenário 2: Superadmin DEVE enviar o ID da escola
        if not aluno.escola_id:
            raise HTTPException(status_code=400, detail="Superadmin deve selecionar uma escola.")
        escola_destino_id = aluno.escola_id
    else:
        # Cenário 1: Admin/Secretária usa a sua própria escola
        escola_destino_id = current_user.escola_id
        if not escola_destino_id: # type: ignore
             raise HTTPException(status_code=400, detail="Utilizador sem escola associada.")

    # Chama o CRUD forçando o ID correto
    return crud_aluno.create_aluno(db=db, aluno=aluno, escola_id=escola_destino_id) # type: ignore

@app.get("/escolas/{escola_id}/alunos", response_model=list[schemas_aluno.AlunoResponse])
def read_alunos_escola(escola_id: int, db: Session = Depends(get_db),
                        current_user: models_user.Usuario = Depends(get_current_user)
                       ):
    """
    Lista todos os alunos de uma escola específica.
    """
    return crud_aluno.get_alunos_by_escola(db=db, escola_id=escola_id)

@app.get("/alunos/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def read_aluno(aluno_id: int, db: Session = Depends(get_db),
               current_user: models_user.Usuario = Depends(get_current_user)):
    # Precisamos desta rota para preencher o formulário de edição
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return aluno

@app.put("/alunos/{aluno_id}", response_model=schemas_aluno.AlunoResponse)
def update_aluno(aluno_id: int, aluno: schemas_aluno.AlunoUpdate, db: Session = Depends(get_db),
                 current_user: models_user.Usuario = Depends(get_current_user)
                ):
    db_aluno = crud_aluno.update_aluno(db=db, aluno_id=aluno_id, aluno_update=aluno)
    if not db_aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return db_aluno

# @app.delete("/alunos/{aluno_id}")
# def delete_aluno(aluno_id: int, db: Session = Depends(get_db),
#                  current_user: models_user.Usuario = Depends(get_current_user)
#                 ):
#     sucesso = crud_aluno.(db=db, aluno_id=aluno_id)
#     if not sucesso:
#         raise HTTPException(status_code=404, detail="Aluno não encontrado")
#     return {"mensagem": "Aluno removido com sucesso"}

# backend/main.py

@app.post("/turmas/", response_model=schemas_turma.TurmaCreate)
def criar_turma(
    turma: schemas_turma.TurmaCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # ID FINAL da escola onde a turma será criada
    escola_destino_id = None

    # CENÁRIO 1: Superadmin (Pode criar para qualquer escola)
    if current_user.perfil == "superadmin": # type: ignore
        if not turma.escola_id:
            # Se o Superadmin esqueceu de dizer a escola, avisamos
            raise HTTPException(status_code=400, detail="Superadmin deve informar o ID da escola.")
        escola_destino_id = turma.escola_id

    # CENÁRIO 2: Admin da Escola / Diretor (Só cria na sua própria escola)
    else:
        # Ignoramos o que vem no JSON e forçamos a escola do login (Segurança)
        escola_destino_id = current_user.escola_id
        
        if not escola_destino_id: # type: ignore
             raise HTTPException(status_code=400, detail="Utilizador não está associado a nenhuma escola.")

    # Chama o CRUD com o ID decidido acima
    return crud_turma.create_turma(db=db, turma=turma, escola_id=escola_destino_id) # type: ignore

@app.get("/escolas/{escola_id}/turmas", response_model=list[schemas_turma.TurmaResponse])
def read_turmas_escola(escola_id: int, db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)

# --- ROTAS PARA DETALHE DE TURMA ---

@app.get("/turmas/{turma_id}", response_model=schemas_turma.TurmaResponse)
def read_turma(turma_id: int, db: Session = Depends(get_db),
               current_user: models_user.Usuario = Depends(get_current_user)):
    db_turma = crud_turma.get_turma(db, turma_id=turma_id)
    if db_turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return db_turma

@app.get("/turmas/", response_model=list[schemas_turma.TurmaResponse])
def ler_turmas(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user) # Importante!
):
    # O Backend força o filtro pela escola do utilizador
    return crud_turma.get_turmas_by_escola(db, escola_id=current_user.escola_id, skip=skip, limit=limit) # type: ignore

@app.get("/turmas/{turma_id}/alunos", response_model=list[schemas_aluno.AlunoResponse])
def read_alunos_turma(turma_id: int, db: Session = Depends(get_db),
                      current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_aluno.get_alunos_por_turma(db=db, turma_id=turma_id)

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
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
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
def read_notas_disciplina(disciplina_id: int, db: Session = Depends(get_db),
                          current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_nota.get_notas_by_disciplina(db=db, disciplina_id=disciplina_id)

@app.get("/alunos/{aluno_id}/boletim", response_model=schemas_boletim.BoletimResponse)
def read_boletim(aluno_id: int, db: Session = Depends(get_db),
                 current_user: models_user.Usuario = Depends(get_current_user)):
    boletim = crud_nota.get_boletim_aluno(db=db, aluno_id=aluno_id)
    if not boletim:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    return boletim

@app.get("/dashboard/stats", response_model=schemas_dashboard.DashboardStats)
def read_dashboard_stats(db: Session = Depends(get_db),
                         current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_dashboard.get_stats(db=db)

# ==========================================
# MÓDULO FINANCEIRO (SaaS Profissional)
# ==========================================

# 1. Gerar Carnet Inteligente (Lê as configurações da Escola)
@app.post("/alunos/{aluno_id}/financeiro/gerar")
def gerar_mensalidades(
    aluno_id: int, 
    ano: int,  # Este parâmetro vem da URL (?ano=2025)
    db: Session = Depends(get_db), 
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # CORREÇÃO AQUI: mudamos 'ano=ano' para 'ano_letivo=ano'
    return crud_mensalidade.gerar_carnet_aluno(
        db=db, 
        aluno_id=aluno_id, 
        ano_letivo=ano,  # <--- O CRUD espera 'ano_letivo'
        current_user_id=current_user.id
    )

# 2. Ver Extrato Financeiro do Aluno
@app.get("/alunos/{aluno_id}/financeiro", response_model=list[schemas_fin.MensalidadeResponse])
def ver_financeiro(
    aluno_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.get_mensalidades_aluno(db=db, aluno_id=aluno_id)

# 3. Efetuar Pagamento (Baixa Financeira)
@app.put("/financeiro/{mensalidade_id}/pagar", response_model=schemas_fin.MensalidadePagar)
def pagar_mensalidade(
    mensalidade_id: int, 
    dados_pagamento: schemas_fin.MensalidadePagar, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # REGRA DE SEGURANÇA:
    # O Frontend manda a forma de pagamento, mas NÓS definimos quem recebeu (o utilizador logado)
    dados_pagamento.pago_por_id = current_user.id
    
    return crud_mensalidade.pagar_mensalidade(db, mensalidade_id, dados_pagamento)

# 4. Imprimir Recibo Único
@app.get("/financeiro/{mensalidade_id}", response_model=schemas_fin.MensalidadeResponse)
def get_recibo(
    mensalidade_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.get_mensalidade(db=db, mensalidade_id=mensalidade_id)
# ==========================================
# FIM DO MÓDULO FINANCEIRO
# ==========================================

@app.put("/auth/me/alterar-senha")
def alterar_senha(
    dados: schemas_user.SenhaUpdate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if not verify_password(dados.senha_atual, str(current_user.senha_hash)): # Adiciona str() para calar o linter se necessário
        raise HTTPException(status_code=400, detail="A senha atual está incorreta.")
    
    # Adiciona o comentário # type: ignore para o Pylance parar de reclamar
    current_user.senha_hash = get_password_hash(dados.nova_senha) # type: ignore
    db.commit()
    
    return {"mensagem": "Senha alterada com sucesso"}

# --- MÓDULO DE ASSIDUIDADE ---

# 1. Salvar a chamada do dia
@app.post("/presencas/", response_model=list[schemas_presenca.PresencaResponse])
def salvar_chamada(
    dados: schemas_presenca.ChamadaDiaria, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_presenca.registrar_chamada(db=db, chamada=dados)

# 2. Ler a chamada de uma turma numa data específica
# Ex: /presencas/turma/5?data=2025-01-22
@app.get("/presencas/turma/{turma_id}", response_model=list[schemas_presenca.PresencaResponse])
def ler_chamada(
    turma_id: int, 
    data: str, # Recebe como string "YYYY-MM-DD"
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    from datetime import datetime
    # Converte string para data real
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    return crud_presenca.get_presencas_dia(db=db, turma_id=turma_id, data_busca=data_obj)

@app.get("/turmas/{turma_id}/alunos", response_model=list[schemas_aluno.AlunoResponse])
def read_alunos_por_turma(turma_id: int, db: Session = Depends(get_db),
                          current_user: models_user.Usuario = Depends(get_current_user)
                          ):
    alunos = crud_aluno.get_alunos_by_turma(db, turma_id=turma_id)
    return alunos

# ==========================================
# MÓDULO DE DISCIPLINAS (CATÁLOGO GERAL N:N)
# ==========================================

# 1. Criar Disciplina (Usa o CRUD corretamente)
@app.post("/disciplinas/", response_model=schemas_disciplina.DisciplinaResponse)
def create_disciplina(
    disciplina: schemas_disciplina.DisciplinaCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_disciplina.create_disciplina(db=db, disciplina=disciplina)


# 2. Listar TODAS as Disciplinas da Escola (Catálogo)
@app.get("/disciplinas/", response_model=list[schemas_disciplina.Disciplina])
def listar_disciplinas(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Nota: Aqui chamei diretamente o modelo pois é uma query simples, 
    # mas o ideal seria criar um crud_disciplina.get_all_disciplinas
    return db.query(models_disciplina.Disciplina).offset(skip).limit(limit).all()


# 3. Listar Disciplinas de UMA Turma Específica
@app.get("/turmas/{turma_id}/disciplinas", response_model=list[schemas_disciplina.DisciplinaResponse])
def read_disciplinas_turma(
    turma_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_disciplina.get_disciplinas_by_turma(db=db, turma_id=turma_id)


# 4. Associar Disciplina Existente a uma Turma
@app.post("/turmas/{turma_id}/associar-disciplina/{disciplina_id}")
def associar_disciplina_a_turma(
    turma_id: int, 
    disciplina_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")

    if disciplina in turma.disciplinas:
        return {"mensagem": "Disciplina já está associada a esta turma"}

    turma.disciplinas.append(disciplina)
    db.commit()

    return {"mensagem": f"Disciplina {disciplina.nome} adicionada à turma {turma.nome}"}

# 5. Remover Disciplina de uma Turma (Desassociar N:N)
@app.delete("/turmas/{turma_id}/remover-disciplina/{disciplina_id}")
def remover_disciplina_de_turma(
    turma_id: int, 
    disciplina_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # 1. Busca a turma e a disciplina
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")

    # 2. Se a disciplina estiver na lista da turma, remove-a
    if disciplina in turma.disciplinas:
        turma.disciplinas.remove(disciplina)
        db.commit()
        return {"mensagem": f"Disciplina {disciplina.nome} removida da turma."}
    
    return {"mensagem": "Esta disciplina já não pertence a esta turma."}

# 3. ATUALIZAR DISCIPLINA (O Lápis)
@app.put("/disciplinas/{disciplina_id}", response_model=schemas_disciplina.Disciplina)
def atualizar_disciplina(
    disciplina_id: int, 
    dados: schemas_disciplina.DisciplinaCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    db_disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()
    if not db_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    
    db_disciplina.nome = dados.nome # type: ignore
    db_disciplina.codigo = dados.codigo # type: ignore
    db_disciplina.carga_horaria = dados.carga_horaria # type: ignore
    
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina


# 4. ELIMINAR DISCIPLINA (O Lixo)
@app.delete("/disciplinas/{disciplina_id}")
def eliminar_disciplina(
    disciplina_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    db_disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()
    if not db_disciplina:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    
    # O SQLAlchemy apaga a disciplina e limpa automaticamente a tabela N:N (turma_disciplina)
    db.delete(db_disciplina)
    db.commit()
    return {"mensagem": "Disciplina eliminada do catálogo e removida de todas as turmas."}

# ==========================================
# MÓDULO DE CONFIGURAÇÕES (Admin da Escola)
# ==========================================

# 1. VER as configurações da minha escola
@app.get("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def ler_minha_configuracao(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # O Segredo: Usa o escola_id do token do utilizador!
    config = crud_configuracao.get_config_by_escola(db, escola_id=current_user.escola_id) # type: ignore
    if not config:
        raise HTTPException(status_code=404, detail="Configuração não encontrada")
    return config

# 2. ATUALIZAR as configurações da minha escola
@app.put("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def atualizar_minha_configuracao(
    dados: schemas_config.ConfiguracaoUpdate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # O Diretor só pode atualizar a configuração da própria escola
    return crud_configuracao.update_config(db=db, escola_id=current_user.escola_id, dados=dados) # type: ignore

# ==========================================
# GESTÃO DOCENTE (Atribuições)
# ==========================================

@app.post("/atribuicoes/", response_model=schemas_atribuicao.AtribuicaoResponse) # Alterado aqui para usar o Response simples se quiseres, ou adapta o crud para devolver o objeto simples na criação
def atribuir_professor(
    dados: schemas_atribuicao.AtribuicaoCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Nota: O create do CRUD retorna o modelo do banco. 
    # O Pydantic vai tentar ler 'turma_nome' mas o modelo acabou de ser criado e as relações podem não estar carregadas.
    # Truque rápido: recarregar ou construir resposta manual.
    # Para simplificar, vamos deixar o Pydantic tentar (se der erro ajustamos o schema de resposta do POST).
    novo = crud_atribuicao.create_atribuicao(db, dados, escola_id=current_user.escola_id) # type: ignore
    
    # Montagem manual segura para resposta imediata
    return {
        "id": novo.id,
        "turma_id": novo.turma_id,
        "disciplina_id": novo.disciplina_id,
        "professor_id": novo.professor_id,
        "turma_nome": novo.turma.nome if novo.turma else "",
        "disciplina_nome": novo.disciplina.nome if novo.disciplina else "",
        "professor_nome": novo.professor.nome if novo.professor else ""
    }

@app.get("/atribuicoes/", response_model=list[schemas_atribuicao.AtribuicaoResponse])
def listar_atribuicoes(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_atribuicao.get_atribuicoes_escola(db, escola_id=current_user.escola_id) # type: ignore

@app.delete("/atribuicoes/{id}")
def remover_atribuicao(
    id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    crud_atribuicao.delete_atribuicao(db, id)
    return {"msg": "Atribuição removida"}

@app.get("/usuarios/professores", response_model=list[schemas_user.UsuarioResponse])
def listar_professores(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Filtra por Escola ID e pelo perfil 'professor'
    return db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == current_user.escola_id,
        models_user.Usuario.perfil == "professor"
    ).all()
    
# Rota para o PROFESSOR ver as suas turmas
@app.get("/minhas-aulas") # O schema de resposta pode ser genérico ou uma lista de dicionários
def ver_minhas_aulas(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Segurança: Apenas professores (ou admins curiosos)
    return crud_atribuicao.get_minhas_atribuicoes(db, professor_id=current_user.id) # type: ignore
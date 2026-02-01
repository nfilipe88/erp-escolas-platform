# app/cruds/crud_escola.py
import re
from sqlalchemy.orm import Session
from app.models import escola as models_escola
from app.models import configuracao as models_config
from app.models import aluno as models_aluno
from app.models import turma as models_turma
from app.models import usuario as models_usuario
from app.schemas import escola as schemas

# --- FUNÇÃO NOVA ADICIONADA ---
def get_escola_by_slug(db: Session, slug: str):
    return db.query(models_escola.Escola).filter(models_escola.Escola.slug == slug).first()
# ------------------------------

# 1. LISTAR TODAS (Leve, para a tabela geral)
def get_escolas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_escola.Escola).offset(skip).limit(limit).all()

# 2. OBTER DETALHES E ESTATÍSTICAS (Pesado, para o Dashboard da Escola)
def get_escola_detalhes(db: Session, escola_id: int):
    # A. Buscar a Escola
    escola = db.query(models_escola.Escola).filter(models_escola.Escola.id == escola_id).first()
    if not escola:
        return None

    # B. Contagem de Alunos
    total_alunos = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.escola_id == escola_id).count()
    # Assumindo que Aluno não tem campo 'ativo' ainda, usamos total. Se tiver, filtramos.
    # Para este exemplo, vou simular que todos são ativos se não houver campo
    alunos_ativos = total_alunos 
    alunos_inativos = 0 

    # C. Contagem de Turmas
    total_turmas = db.query(models_turma.Turma).filter(models_turma.Turma.escola_id == escola_id).count()

    # D. Contagem de Usuários e Perfis
    usuarios_query = db.query(models_usuario.Usuario).filter(models_usuario.Usuario.escola_id == escola_id)
    total_usuarios = usuarios_query.count()
    
    # Agrupar por perfil (ex: professor, secretaria, admin)
    perfis = ["admin", "professor", "secretaria"]
    contagem_perfis = {}
    for p in perfis:
        qtd = usuarios_query.filter(models_usuario.Usuario.perfil == p).count()
        contagem_perfis[p] = qtd

    # E. Buscar quem são os Diretores/Admins
    diretores = usuarios_query.filter(models_usuario.Usuario.perfil == "admin").all()

    # F. Montar o Objeto de Resposta
    return {
        **escola.__dict__, # Copia dados básicos (nome, slug, endereco...)
        "total_alunos": total_alunos,
        "alunos_ativos": alunos_ativos,
        "alunos_inativos": alunos_inativos,
        "total_turmas": total_turmas,
        "total_usuarios": total_usuarios,
        "contagem_por_perfil": contagem_perfis,
        "lista_diretores": diretores
    }

# Função auxiliar para criar slug
def gerar_slug(nome: str) -> str:
    slug = nome.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug

def create_escola(db: Session, escola: schemas.EscolaCreate):
    # 1. Gerar Slug Automático se não vier preenchido
    slug_final = escola.slug
    if not slug_final:
        slug_final = gerar_slug(escola.nome)
        
        # Verificar se já existe e adicionar sufixo
        contador = 1
        slug_original = slug_final
        while db.query(models_escola.Escola).filter(models_escola.Escola.slug == slug_final).first():
            slug_final = f"{slug_original}-{contador}"
            contador += 1

    # 2. Cria a Escola (Identidade)
    db_escola = models_escola.Escola(
        nome=escola.nome,
        slug=slug_final,
        endereco=escola.endereco,
        telefone=escola.telefone,
        email=escola.email,
        is_active=True # Garante que nasce ativa
    )
    db.add(db_escola)
    db.commit()
    db.refresh(db_escola)

    # 3. MAGIA SEGURA: Cria Configuração (Verificando se já existe para evitar erro 500)
    # Verifica se já existe uma config para este ID (pode ser lixo de banco ou trigger)
    config_existente = db.query(models_config.Configuracao).filter(
        models_config.Configuracao.escola_id == db_escola.id
    ).first()

    if not config_existente:
        db_config = models_config.Configuracao(
            escola_id=db_escola.id
            # Os outros campos assumem os valores default definidos no Modelo
        )
        db.add(db_config)
        db.commit()

    return db_escola
# app/cruds/crud_escola.py
import re
from sqlalchemy.orm import Session
from app.models import escola as models_escola
from app.models import configuracao as models_config
from app.models import aluno as models_aluno
from app.models import turma as models_turma
from app.models import usuario as models_usuario
from app.schemas import schema_escola

def get_escola_by_slug(db: Session, slug: str):
    return db.query(models_escola.Escola).filter(models_escola.Escola.slug == slug).first()

def get_escolas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models_escola.Escola).offset(skip).limit(limit).all()

def get_escola_detalhes(db: Session, escola_id: int):
    escola = db.query(models_escola.Escola).filter(models_escola.Escola.id == escola_id).first()
    if not escola:
        return None

    total_alunos = db.query(models_aluno.Aluno).filter(
        models_aluno.Aluno.escola_id == escola_id
    ).count()
    alunos_ativos = db.query(models_aluno.Aluno).filter(
        models_aluno.Aluno.escola_id == escola_id,
        models_aluno.Aluno.ativo == True
    ).count()
    alunos_inativos = total_alunos - alunos_ativos

    total_turmas = db.query(models_turma.Turma).filter(
        models_turma.Turma.escola_id == escola_id
    ).count()

    usuarios_query = db.query(models_usuario.Usuario).filter(
        models_usuario.Usuario.escola_id == escola_id
    )
    total_usuarios = usuarios_query.count()

    perfis = ["admin", "professor", "secretaria"]
    contagem_perfis = {}
    for p in perfis:
        qtd = usuarios_query.filter(models_usuario.Usuario.perfil == p).count()
        contagem_perfis[p] = qtd

    diretores = usuarios_query.filter(models_usuario.Usuario.perfil == "admin").all()

    return {
        **escola.__dict__,
        "total_alunos": total_alunos,
        "alunos_ativos": alunos_ativos,
        "alunos_inativos": alunos_inativos,
        "total_turmas": total_turmas,
        "total_usuarios": total_usuarios,
        "contagem_por_perfil": contagem_perfis,
        "lista_diretores": diretores
    }

def gerar_slug(nome: str) -> str:
    slug = nome.lower().strip()
    slug = re.sub(r'[^A-Z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug

def create_escola(db: Session, escola: schema_escola.EscolaCreate):
    slug_final = escola.slug
    if not slug_final:
        slug_final = gerar_slug(escola.nome)
        contador = 1
        slug_original = slug_final
        while db.query(models_escola.Escola).filter(models_escola.Escola.slug == slug_final).first():
            slug_final = f"{slug_original}-{contador}"
            contador += 1

    db_escola = models_escola.Escola(
        nome=escola.nome,
        slug=slug_final,
        endereco=escola.endereco,
        telefone=escola.telefone,
        email=escola.email,
        is_active=True
    )
    db.add(db_escola)
    db.commit()
    db.refresh(db_escola)

    config_existente = db.query(models_config.Configuracao).filter(
        models_config.Configuracao.escola_id == db_escola.id
    ).first()

    if not config_existente:
        db_config = models_config.Configuracao(escola_id=db_escola.id)
        db.add(db_config)
        db.commit()

    return db_escola
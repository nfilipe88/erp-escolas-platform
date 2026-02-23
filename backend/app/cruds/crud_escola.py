# app/cruds/crud_escola.py
import re
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import escola as models_escola
from app.models import configuracao as models_config
from app.models import aluno as models_aluno
from app.models import turma as models_turma
from app.models import usuario as models_usuario
from app.models.role import Role
from app.models.usuario_roles import usuario_roles
from app.schemas import schema_escola

def get_escola_by_slug(db: Session, slug: str):
    return db.query(models_escola.Escola).filter(models_escola.Escola.slug == slug).first()

def get_escola_by_id(db: Session, escola_id: int):
    return db.query(models_escola.Escola).filter(models_escola.Escola.id == escola_id).first()

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

    total_usuarios = db.query(models_usuario.Usuario).filter(
        models_usuario.Usuario.escola_id == escola_id
    ).count()

    # Contagem de utilizadores por role (perfil)
    contagem = db.query(
        Role.name,
        func.count(usuario_roles.c.usuario_id).label('count')
    ).join(
        usuario_roles, Role.id == usuario_roles.c.role_id
    ).join(
        models_usuario.Usuario, models_usuario.Usuario.id == usuario_roles.c.usuario_id
    ).filter(
        models_usuario.Usuario.escola_id == escola_id
    ).group_by(Role.name).all()

    contagem_por_perfil = {nome: qtd for nome, qtd in contagem}

    # Lista de diretores (utilizadores com role 'admin')
    diretores = db.query(models_usuario.Usuario).join(
        usuario_roles, models_usuario.Usuario.id == usuario_roles.c.usuario_id
    ).join(
        Role, Role.id == usuario_roles.c.role_id
    ).filter(
        models_usuario.Usuario.escola_id == escola_id,
        Role.name == 'admin'
    ).all()

    lista_diretores = [
        {
            "id": d.id,
            "nome": d.nome,
            "email": d.email,
            "perfil": "admin"
        }
        for d in diretores
    ]

    return {
        **escola.__dict__,
        "total_alunos": total_alunos,
        "alunos_ativos": alunos_ativos,
        "alunos_inativos": alunos_inativos,
        "total_turmas": total_turmas,
        "total_usuarios": total_usuarios,
        "contagem_por_perfil": contagem_por_perfil,
        "lista_diretores": lista_diretores
    }

def gerar_slug(nome: str) -> str:
    slug = nome.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
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

    # Criar configuração padrão para a escola
    config_existente = db.query(models_config.Configuracao).filter(
        models_config.Configuracao.escola_id == db_escola.id
    ).first()
    if not config_existente:
        db_config = models_config.Configuracao(escola_id=db_escola.id)
        db.add(db_config)
        db.commit()

    return db_escola
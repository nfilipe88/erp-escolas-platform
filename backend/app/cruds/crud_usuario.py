from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models import usuario as models_user
from app.models.role import Role
from app.schemas import schema_usuario as schemas_user
from app.security import get_password_hash

def get_usuario_by_email(db: Session, email: str):
    return db.query(models_user.Usuario).filter(models_user.Usuario.email == email).first()

def get_usuarios_por_escola(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    return db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == escola_id
    ).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schemas_user.UsuarioCreate, escola_id: int = None, roles_ids: list[int] = None):
    # 1. Criar o utilizador
    db_user = models_user.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=get_password_hash(usuario.senha),
        escola_id=escola_id,
        ativo=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 2. REGRA DE NEGÓCIO: Atribuição de Roles
    if roles_ids and len(roles_ids) > 0:
        # Se enviaram roles específicas, atribuir
        for r_id in roles_ids:
            role = db.query(Role).filter(Role.id == r_id).first()
            if role:
                db_user.roles.append(role)
    else:
        # Se NÃO enviaram roles, dar "visitante" obrigatoriamente
        visitante_role = db.query(Role).filter(
            (Role.name == 'visitante') | (Role.name == 'visitante')
        ).first()
        
        # Se a role "visitante" ainda não existir na base de dados, o sistema cria-a automaticamente
        if not visitante_role:
            visitante_role = Role(name='visitante', descricao='Acesso limitado de visitante')
            db.add(visitante_role)
            db.commit()
            db.refresh(visitante_role)
            
        db_user.roles.append(visitante_role)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def get_usuarios(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models_user.Usuario).options(joinedload(models_user.Usuario.roles))
    if escola_id:
        query = query.filter(models_user.Usuario.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()
# app/cruds/crud_usuario.py
from sqlalchemy.orm import Session
from app.models import usuario as models
from app.schemas import schema_usuario
from app.security import get_password_hash
from typing import Optional

def get_usuario_by_email(db: Session, email: str, escola_id: Optional[int] = None):
    query = db.query(models.Usuario).filter(models.Usuario.email == email)
    if escola_id:
        query = query.filter(models.Usuario.escola_id == escola_id)
    return query.first()

def get_usuarios_por_escola(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).filter(
        models.Usuario.escola_id == escola_id
    ).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schema_usuario.UsuarioCreate, escola_id: int):
    hashed_password = get_password_hash(usuario.senha)
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hashed_password,
        perfil=usuario.perfil.value,  # converte Enum para string
        escola_id=escola_id,
        ativo=usuario.ativo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_usuarios(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models.Usuario)
    if escola_id:
        query = query.filter(models.Usuario.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()
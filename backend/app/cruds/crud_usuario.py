from sqlalchemy.orm import Session
from app.models import usuario as models
from app.schemas import schema_usuario
from app.security import get_password_hash

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_usuarios_por_escola(db: Session, skip: int = 0, limit: int = 100, escola_id: int = None):
    query = db.query(models.Usuario)
    
    if escola_id:
        query = query.filter(models.Usuario.escola_id == escola_id)
        
    return query.offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schema_usuario.UsuarioCreate, escola_id: int):
    hashed_password = get_password_hash(usuario.senha)
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hashed_password,
        perfil=usuario.perfil,
        escola_id=escola_id, # <--- Vincula à escola correta
        ativo=usuario.ativo
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def get_usuarios(db: Session, skip: int = 0, limit: int = 100, escola_id: int = None):
    query = db.query(models.Usuario)
    
    if escola_id:
        query = query.filter(models.Usuario.escola_id == escola_id)
        
    return query.offset(skip).limit(limit).all()
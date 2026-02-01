from sqlalchemy.orm import Session
from app.models import usuario as models
from app.schemas import usuario as schemas
from app.security import get_password_hash

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_usuarios_por_escola(db: Session, escola_id: int):
    return db.query(models.Usuario).filter(models.Usuario.escola_id == escola_id).all()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate, escola_id: int):
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
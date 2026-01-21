from sqlalchemy.orm import Session
from app.models import usuario as models
from app.schemas import usuario as schemas
from app.security import get_password_hash

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    # Encripta a senha antes de salvar
    senha_encriptada = get_password_hash(usuario.senha)
    
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil,
        senha_hash=senha_encriptada
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario
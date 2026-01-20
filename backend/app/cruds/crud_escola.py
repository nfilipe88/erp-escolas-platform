# backend/app/crud.py
from sqlalchemy.orm import Session
from app.models import escola as models
from app.schemas import escola as schemas

# Função para verificar se já existe uma escola com esse Slug
def get_escola_by_slug(db: Session, slug: str):
    return db.query(models.Escola).filter(models.Escola.slug == slug).first()

# Função para criar a escola
def create_escola(db: Session, escola: schemas.EscolaCreate):
    # Transforma o Schema Pydantic num Modelo SQLAlchemy
    db_escola = models.Escola(
        nome=escola.nome,
        slug=escola.slug,
        endereco=escola.endereco
    )
    db.add(db_escola)
    db.commit()
    db.refresh(db_escola)
    return db_escola
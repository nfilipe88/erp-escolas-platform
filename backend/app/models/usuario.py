from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    
    # Perfil: 'admin' (Diretor), 'professor', 'secretaria'
    perfil = Column(String, default="professor") 
    ativo = Column(Boolean, default=True)
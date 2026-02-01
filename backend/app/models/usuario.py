from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=True) # Pode ser Null para o Superadmin
    escola = relationship("Escola", back_populates="usuarios")
    
    # Perfil: 'admin' (Diretor), 'professor', 'secretaria', 'superadmin'
    perfil = Column(String, default="professor") 
    ativo = Column(Boolean, default=True)
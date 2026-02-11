from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

import enum
class PerfilUsuario(enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    SECRETARIA = "secretaria"
    PROFESSOR = "professor"
    
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    
    escola_id = Column(Integer, ForeignKey("escolas.id"), ondelete="CASCADE", nullable=True, index=True) # Pode ser Null para o Superadmin
    
    escola = relationship("Escola", back_populates="usuarios")
    diarios = relationship("Diario", back_populates="professor")
    horarios = relationship("Horario", back_populates="professor")
    atribuicoes = relationship("Atribuicao", back_populates="professor")
    ponto_professores = relationship("PontoProfessor", back_populates="professor")
    
    # Perfil: 'admin' (Diretor), 'professor', 'secretaria', 'superadmin'
    perfil = Column(Enum(PerfilUsuario), default=PerfilUsuario.PROFESSOR)
    ativo = Column(Boolean, default=True)
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
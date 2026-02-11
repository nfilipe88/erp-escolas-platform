from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Aluno(Base):
    __tablename__ = "alunos"

    # Dados Pessoais
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True, nullable=False)
    bi = Column(String, unique=True, index=True, nullable=True) # Bilhete de Identidade
    data_nascimento = Column(Date, nullable=True)
    
    # RELACIONAMENTO (A chave mágica 🗝️)
    # Aqui dizemos: "Este aluno pertence à escola com este ID"
    escola_id = Column(Integer, ForeignKey("escolas.id"), ondelete="CASCADE", nullable=False, index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=True)
    
    # Dados de Controlo
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Vínculo bidirecional (para acederes a aluno.escola)
    escola = relationship("Escola", back_populates="alunos")
    turma = relationship("Turma", back_populates="alunos")
    notas = relationship("Nota", back_populates="aluno", cascade="all, delete-orphan")
    mensalidades = relationship("Mensalidade", back_populates="aluno", cascade="all, delete-orphan")
    presencas = relationship("Presenca", back_populates="aluno", cascade="all, delete-orphan")
from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    valor = Column(Float, nullable=False)       # Ex: 14.5
    trimestre = Column(String, nullable=False)  # Ex: "1º Trimestre"
    descricao = Column(String, nullable=True)   # Ex: "Prova 1", "Trabalho"
    # Guarda o caminho do ficheiro (pode ser nulo)
    arquivo_url = Column(String, nullable=True)
    data_avaliacao = Column(Date, server_default=func.now())
    
    # Chaves Estrangeiras (A nota pertence a um aluno numa disciplina)
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False, index=True)
    escola_id = Column(Integer, ForeignKey("escolas.id"), ondelete="CASCADE", nullable=False, index=True) # Para garantir que cada nota pertence a uma escola específica (multi-tenancy)
    
    # Relações
    escola = relationship("Escola", back_populates="notas")
    disciplina = relationship("Disciplina", back_populates="notas")
    aluno = relationship("Aluno", back_populates="notas", cascade="all, delete-orphan")

    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
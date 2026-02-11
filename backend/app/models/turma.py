from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from backend.app.models.associacoes import turma_disciplina # Importa a tabela ponte   
class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)      # Ex: "10ª Classe A"
    ano_letivo = Column(String, nullable=False) # Ex: "2024"
    turno = Column(String, nullable=True)       # Ex: "Manhã"

    # Relacionamento com Escola
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=False)

    # Relacionamento com Alunos (Uma turma tem vários alunos)
    escola = relationship("Escola", back_populates="turmas", cascade="all, delete-orphan")
    alunos = relationship("Aluno", back_populates="turma", cascade="all, delete-orphan")
    disciplinas = relationship("Disciplina", secondary=turma_disciplina, back_populates="turmas")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
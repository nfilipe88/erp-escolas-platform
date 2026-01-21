from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)      # Ex: "10ª Classe A"
    ano_letivo = Column(String, nullable=False) # Ex: "2024"
    turno = Column(String, nullable=True)       # Ex: "Manhã"

    # Relacionamento com Escola
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=False)
    escola = relationship("Escola", back_populates="turmas")

    # Relacionamento com Alunos (Uma turma tem vários alunos)
    alunos = relationship("Aluno", back_populates="turma")
    disciplinas = relationship("Disciplina", back_populates="turma")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
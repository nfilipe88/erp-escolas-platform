from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.turma import turma_disciplina # Importa a tabela ponte

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False) # Ex: "Matemática", "Língua Portuguesa"
    codigo = Column(String, unique=True, index=True, nullable=False) 
    carga_horaria = Column(Integer, default=80)

    # 1. Relacionamento de volta para as turmas (N:N)
    turmas = relationship("Turma", secondary=turma_disciplina, back_populates="disciplinas")
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=False) 
    
    # Relacionamentos
    notas = relationship("Nota", back_populates="disciplina")
    escola = relationship("Escola", back_populates="disciplinas")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
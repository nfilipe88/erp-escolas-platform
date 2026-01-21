from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False) # Ex: "Matemática", "Língua Portuguesa"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Pertence a uma turma específica
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    
    # Relacionamento
    turma = relationship("Turma", back_populates="disciplinas")
    notas = relationship("Nota", back_populates="disciplina")
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False) # Ex: "Matemática", "Língua Portuguesa"
    
    # Pertence a uma turma específica
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    
    # Relacionamento
    turma = relationship("Turma", back_populates="disciplinas")
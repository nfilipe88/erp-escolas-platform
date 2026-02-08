from sqlalchemy import Column, Integer, Date, ForeignKey, Boolean, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Presenca(Base):
    __tablename__ = "presencas"

    id = Column(Integer, primary_key=True, index=True)
    
    data = Column(Date, nullable=False)
    presente = Column(Boolean, default=True)      # True = Veio, False = Faltou
    justificado = Column(Boolean, default=False)  # Se faltou, tem justificação?
    observacao = Column(String, nullable=True)    # Ex: "Chegou atrasado"
    status = Column(String, nullable=True)      # 'P', 'F', 'FJ'

    # Relacionamentos
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    
    aluno = relationship("Aluno")
    turma = relationship("Turma")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
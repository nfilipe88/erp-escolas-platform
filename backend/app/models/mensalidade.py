from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Mensalidade(Base):
    __tablename__ = "mensalidades"

    id = Column(Integer, primary_key=True, index=True)
    
    # O que é que se está a pagar?
    mes = Column(String, nullable=False)   # Ex: "Janeiro"
    ano = Column(Integer, nullable=False)  # Ex: 2025
    valor_base = Column(Float, nullable=False) # Quanto custa a propina?
    
    # Estado do Pagamento
    estado = Column(String, default="Pendente") # "Pendente", "Pago", "Atrasado"
    data_pagamento = Column(Date, nullable=True)
    forma_pagamento = Column(String, nullable=True) # "Multicaixa", "Numerário"
    
    # Relacionamento com Aluno
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    aluno = relationship("Aluno", back_populates="mensalidades")

    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
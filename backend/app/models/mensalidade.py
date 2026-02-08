from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import date, datetime
from sqlalchemy.sql import func
from app.db.database import Base

class Mensalidade(Base):
    __tablename__ = "mensalidades"

    id = Column(Integer, primary_key=True, index=True)
    
    # Dados da Fatura
    # O que é que se está a pagar?
    descricao = Column(String, nullable=False) 
    mes = Column(String, nullable=False)   # Ex: "Janeiro"
    ano = Column(Integer, nullable=False)  # Ex: 2025
    valor_base = Column(Float, nullable=False) # Quanto custa a propina?
    
    # Datas Críticas
    data_emissao = Column(Date, default=date.today)
    data_vencimento = Column(Date, nullable=False)
    
    # Estado do Pagamento
    estado = Column(String, default="Pendente") # "Pendente", "Pago", "Atrasado"
    data_pagamento = Column(Date, nullable=True)
    forma_pagamento = Column(String, nullable=True) # "Multicaixa", "Numerário"
    
    # Auditoria (Quem fez o quê?)
    criado_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])
    pago_por_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    pago_por = relationship("Usuario", foreign_keys=[pago_por_id])
    
    # Relacionamento com Aluno
    aluno_id = Column(Integer, ForeignKey("alunos.id"), nullable=False)
    aluno = relationship("Aluno", back_populates="mensalidades")
    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False)
    escola = relationship("Escola")

    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
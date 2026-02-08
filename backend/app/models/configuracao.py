# app/models/configuracao.py
from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Configuracao(Base):
    __tablename__ = "configuracoes_escola"

    id = Column(Integer, primary_key=True, index=True)    
    # RELAÇÃO 1:1 COM A ESCOLA (unique=True garante que cada escola só tem 1 configuração)
    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), unique=True, nullable=False)
    # --- REGRAS FINANCEIRAS ---
    valor_mensalidade_padrao = Column(Float, default=35000.0)
    dia_vencimento = Column(Integer, default=10) # Dia limite
    multa_atraso_percentual = Column(Float, default=5.0) # 5% de multa
    desconto_pagamento_anual = Column(Float, default=10.0) # 10% de desconto
    mes_inicio_cobranca = Column(Integer, default=9) # Setembro
    mes_fim_cobranca = Column(Integer, default=7)    # Julho
    bloquear_boletim_devedor = Column(Boolean, default=False) # Futuro: Bloqueia notas se não pagar
    texto_recibo = Column(String, default="Obrigado pelo seu pagamento. ERP Pige.")
    # --- REGRAS ACADÉMICAS (Futuro) ---
    nota_minima_aprovacao = Column(Float, default=10.0) # Algumas escolas exigem 10, outras 14
    # Relação de volta
    escola = relationship("Escola", back_populates="configuracao")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
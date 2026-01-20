# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.orm import relationship

class Escola(Base):
    __tablename__ = "escolas"

    # 1. Identificação da Escola
    # index=True torna as pesquisas por ID muito rápidas
    id = Column(Integer, primary_key=True, index=True)
    
    # Nome da escola (ex: "Colégio Futuro")
    nome = Column(String, index=True, nullable=False)
    
    # Slug é útil para URLs (ex: escola.com/colegio-futuro) e identificação única
    slug = Column(String, unique=True, index=True, nullable=False)
    
    # 2. Dados de Controlo
    endereco = Column(String, nullable=True)
    ativo = Column(Boolean, default=True) # Se a escola deixar de pagar, mudamos para False
    
    # 3. Auditoria (Quando foi criada/atualizada)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    alunos = relationship("Aluno", back_populates="escola")
    # Nota: Futuramente, adicionaremos aqui relacionamentos (ex: alunos = relationship(...))
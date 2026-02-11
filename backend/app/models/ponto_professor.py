
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class PontoProfessor(Base):
    __tablename__ = "ponto_professores"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, index=True)
    presente = Column(Boolean, default=True)
    observacao = Column(String, nullable=True)
    
    professor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True) # Para garantir que cada ponto pertence a um professor específico
    escola_id = Column(Integer, ForeignKey("escolas.id"),ondelete="CASCADE", nullable=False, index=True) # Para garantir que cada ponto pertence a uma escola específica (multi-tenancy)
    # Relações
    escola = relationship("Escola", back_populates="ponto_professores")
    professor = relationship("Usuario", back_populates="ponto_professores")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
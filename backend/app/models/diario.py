
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Diario(Base):
    __tablename__ = "diarios"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date, index=True)
    resumo_aula = Column(Text, nullable=True) # O professor escreve o sumário
    fechado = Column(Boolean, default=False)  # Se True, professor não edita mais (foi enviado à secretaria)
    
    horario_id = Column(Integer, ForeignKey("horarios.id"), nullable=False, index=True)
    professor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False, index=True) 
    
    # Relacionamentos
    escola = relationship("Escola", back_populates="diarios")
    horario = relationship("Horario", back_populates="diarios")
    professor = relationship("Usuario", back_populates="diarios")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
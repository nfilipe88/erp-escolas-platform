
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Diario(Base):
    __tablename__ = "diarios"

    id = Column(Integer, primary_key=True, index=True)
    horario_id = Column(Integer, ForeignKey("horarios.id"))
    professor_id = Column(Integer, ForeignKey("usuarios.id")) # Quem deu a aula
    data = Column(Date)
    
    resumo_aula = Column(Text, nullable=True) # O professor escreve o sumário
    fechado = Column(Boolean, default=False)  # Se True, professor não edita mais (foi enviado à secretaria)
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=False) 
    
    # Relações
    
    # Relacionamentos
    escola = relationship("Escola", back_populates="diarios")
    horario = relationship("Horario")
    professor = relationship("Usuario")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
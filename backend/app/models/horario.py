# app/models/horario.py
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    escola_id = Column(Integer, ForeignKey("escolas.id"))
    turma_id = Column(Integer, ForeignKey("turmas.id"))
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"))
    professor_id = Column(Integer, ForeignKey("usuarios.id")) # O professor atribuído a este horário
    dia_semana = Column(Integer) # 0=Segunda, 1=Terça... 4=Sexta
    hora_inicio = Column(Time)   # Ex: 08:00
    hora_fim = Column(Time)      # Ex: 08:45
    
    # Relacionamentos
    turma = relationship("Turma", back_populates="horarios", cascade="all, delete-orphan")
    disciplina = relationship("Disciplina", back_populates="horarios", cascade="all, delete-orphan")
    professor = relationship("Usuario", back_populates="horarios", cascade="all, delete-orphan")
    escola = relationship("Escola", back_populates="horarios", cascade="all, delete-orphan")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
# app/models/atribuicao.py
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Atribuicao(Base):
    __tablename__ = "atribuicoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. Segurança SaaS (Sempre!)
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=False)

    # 2. A Trindade Académica
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False)
    professor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    # Relacionamentos (para podermos aceder aos nomes depois)
    escola = relationship("Escola", back_populates="atribuicoes", cascade="all, delete-orphan")
    turma = relationship("Turma", back_populates="atribuicoes", cascade="all, delete-orphan")
    disciplina = relationship("Disciplina", back_populates="atribuicoes", cascade="all, delete-orphan")
    professor = relationship("Usuario", back_populates="atribuicoes", cascade="all, delete-orphan")

    # Regra de Ouro: Numa turma, uma disciplina só pode ter UM professor titular
    # (Evita duplicados como "João dá Mat na 7A" e "Maria dá Mat na 7A" ao mesmo tempo)
    __table_args__ = (
        UniqueConstraint('turma_id', 'disciplina_id', name='unica_disciplina_por_turma'),
    )
    
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
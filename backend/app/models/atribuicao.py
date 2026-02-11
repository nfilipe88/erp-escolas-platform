from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Atribuicao(Base):
    __tablename__ = "atribuicoes"

    id = Column(Integer, primary_key=True, index=True)

    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False, index=True)

    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=False, index=True)
    disciplina_id = Column(Integer, ForeignKey("disciplinas.id"), nullable=False, index=True)
    professor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)

    escola = relationship("Escola", back_populates="atribuicoes")
    turma = relationship("Turma", back_populates="atribuicoes")
    disciplina = relationship("Disciplina", back_populates="atribuicoes")
    professor = relationship("Usuario", back_populates="atribuicoes")

    # 🔐 Unicidade: por turma e disciplina (professor único por disciplina naquela turma)
    __table_args__ = (
        UniqueConstraint('turma_id', 'disciplina_id', name='unica_disciplina_por_turma'),
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
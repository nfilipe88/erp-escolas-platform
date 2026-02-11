from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.associacoes import turma_disciplina

class Disciplina(Base):
    __tablename__ = "disciplinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    codigo = Column(String, nullable=False)  # ← removido unique=True
    carga_horaria = Column(Integer, default=80)

    turmas = relationship("Turma", secondary=turma_disciplina, back_populates="disciplinas")
    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relacionamentos
    notas = relationship("Nota", back_populates="disciplina", cascade="all, delete-orphan")
    escola = relationship("Escola", back_populates="disciplinas")
    horarios = relationship("Horario", back_populates="disciplina")
    atribuicoes = relationship("Atribuicao", back_populates="disciplina")

    # 🔐 Unicidade: código único DENTRO da mesma escola
    __table_args__ = (
        UniqueConstraint('codigo', 'escola_id', name='uq_disciplina_codigo_escola'),
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
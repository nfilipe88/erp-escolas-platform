from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from app.models.associacoes import turma_disciplina

class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    ano_letivo = Column(String, nullable=False, index=True)
    turno = Column(String, nullable=True)

    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False, index=True)

    escola = relationship("Escola", back_populates="turmas")
    alunos = relationship("Aluno", back_populates="turma", cascade="all, delete-orphan")
    disciplinas = relationship("Disciplina", secondary=turma_disciplina, back_populates="turmas")
    horarios = relationship("Horario", back_populates="turma")
    presencas = relationship("Presenca", back_populates="turma")
    atribuicoes = relationship("Atribuicao", back_populates="turma")

    # 🔐 Unicidade: não pode haver duas turmas com mesmo nome e ano letivo na mesma escola
    __table_args__ = (
        UniqueConstraint('nome', 'ano_letivo', 'escola_id', name='uq_turma_nome_ano_escola'),
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
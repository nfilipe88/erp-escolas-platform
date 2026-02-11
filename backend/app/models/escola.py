# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
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
    telefone = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    
    # 2. Dados de Controlo
    endereco = Column(String, nullable=True)
    is_active = Column(Boolean, default=True) # Se a escola deixar de pagar, mudamos para False
    
    # 3. Auditoria (Quando foi criada/atualizada)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    alunos = relationship("Aluno", back_populates="escola", cascade="all, delete-orphan")
    turmas = relationship("Turma", back_populates="escola", cascade="all, delete-orphan")
    usuarios = relationship("Usuario", back_populates="escola", cascade="all, delete-orphan")
    horarios = relationship("Horario", back_populates="escola", cascade="all, delete-orphan")
    notas = relationship("Nota", back_populates="escola", cascade="all, delete-orphan")
    presencas = relationship("Presenca", back_populates="escola", cascade="all, delete-orphan")
    diarios = relationship("Diario", back_populates="escola", cascade="all, delete-orphan")
    ponto_professores = relationship("PontoProfessor", back_populates="escola", cascade="all, delete-orphan")
    mensalidades = relationship("Mensalidade", back_populates="escola", cascade="all, delete-orphan")
    atribuicoes = relationship("Atribuicao", back_populates="escola", cascade="all, delete-orphan")
    disciplinas = relationship("Disciplina", back_populates="escola", cascade="all, delete-orphan")
    configuracao = relationship("Configuracao", back_populates="escola", uselist=False, cascade="all, delete-orphan")
    
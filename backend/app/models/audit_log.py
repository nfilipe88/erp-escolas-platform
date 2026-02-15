# backend/app/models/audit_log.py - NOVO ARQUIVO
from sqlalchemy import Boolean, Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    """Registro de todas as ações no sistema"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Quem fez
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    usuario_email = Column(String, nullable=False)  # Denormalizado para histórico
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=True, index=True)
    
    # O que foi feito
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN, etc.
    entity_type = Column(String(50), nullable=True, index=True)  # Aluno, Turma, Nota, etc.
    entity_id = Column(Integer, nullable=True, index=True)
    
    # Detalhes
    changes = Column(JSON, nullable=True)  # Diff do antes/depois
    metadata = Column(JSON, nullable=True)  # Info adicional (IP, user agent, etc.)
    
    # Quando
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    
    # Índices compostos para queries comuns
    __table_args__ = (
        Index('idx_audit_usuario_timestamp', 'usuario_id', 'timestamp'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_escola_timestamp', 'escola_id', 'timestamp'),
    )
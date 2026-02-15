# backend/app/models/permission.py - NOVO ARQUIVO
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models import role_permissions

# Tabela associativa para roles e permissions (many-to-many)

class Permission(Base):
    """Permissão granular no sistema"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    resource = Column(String, nullable=False, index=True)  # alunos, notas, etc
    action = Column(String, nullable=False, index=True)  # create, read, update, delete
    description = Column(String, nullable=True)
    
    # Relações
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models import role_permissions

class Role(Base):
    """Papel/Perfil com múltiplas permissões"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_system_role = Column(Boolean, default=False)  # Não pode ser deletado
    escola_id = Column(Integer, ForeignKey('escolas.id'), nullable=True)
    
    # Relações
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    usuarios = relationship("Usuario", back_populates="role")
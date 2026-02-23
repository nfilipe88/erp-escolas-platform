from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.models.role_permissions import role_permissions # Tabela pivot role<->permission
from app.models.usuario_roles import usuario_roles # Tabela pivot usuario<->role

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # ou 'nome'
    description = Column(String) # ou 'descricao'
    is_system_role = Column(Boolean, default=False)
    
    # Se escola_id for NULL, é uma Role global do sistema (ex: SuperAdmin)
    # Se tiver ID, é uma Role personalizada daquela escola
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=True)
    # Para saber a que escola pertence a customização
    escola = relationship("Escola", back_populates="roles_personalizadas")

    # Relacionamento com Usuários (Many-to-Many)
    usuarios = relationship("Usuario", secondary=usuario_roles, back_populates="roles")
    
    # Relacionamento com Permissões (Many-to-Many)
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    
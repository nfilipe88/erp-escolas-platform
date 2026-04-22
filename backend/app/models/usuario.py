from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base
# Importar a tabela associativa (certifique-se que o caminho está correto)
from app.models.usuario_roles import usuario_roles 

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)
    escola_id = Column(Integer, ForeignKey("escolas.id"), nullable=True) # Pode ser Null para superadmin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # --- RELACIONAMENTOS ---
    
    # RBAC: Relacionamento Many-to-Many com Roles
    # 'secondary' aponta para a tabela de associação
    # 'back_populates' deve corresponder ao nome do relacionamento no modelo Role
    roles = relationship("Role", secondary=usuario_roles, back_populates="usuarios") 
    
    escola = relationship("Escola", back_populates="usuarios")
    notificacoes = relationship("Notificacao", back_populates="usuario", cascade="all, delete-orphan")
    
    # Outros relacionamentos (mantenha os que já existiam e estão corretos)
    roles = relationship("Role", secondary=usuario_roles, back_populates="usuarios", lazy="selectin")
    diarios = relationship("Diario", back_populates="professor")
    horarios = relationship("Horario", back_populates="professor")
    atribuicoes = relationship("Atribuicao", back_populates="professor")
    ponto_professores = relationship("PontoProfessor", back_populates="professor")

    @property
    def lista_permissoes(self):
        """
        Retorna um set com TODAS as strings de permissão acumuladas de todas as roles.
        """
        perms = set()
        for role in self.roles:
            for permission in role.permissions:
                perms.add(permission.name) # Use .name ou .nome conforme seu modelo Permission
        return perms
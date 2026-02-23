from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

# Tabela de ligação: Usuario <-> Role
usuario_roles = Table(
    'usuario_roles',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('usuarios.id', ondelete="CASCADE"), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True)
)
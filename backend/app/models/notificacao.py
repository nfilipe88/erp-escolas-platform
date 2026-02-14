from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    mensagem = Column(String)
    lida = Column(Boolean, default=False)
    data_criacao = Column(DateTime, default=datetime.now)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True) # Destinatário
    escola_id = Column(Integer, ForeignKey("escolas.id", ondelete="CASCADE"), nullable=False, index=True) 
    
    # Relacionamentos
    escola = relationship("Escola", back_populates="notificacoes")
    usuario = relationship("Usuario", back_populates="notificacoes")
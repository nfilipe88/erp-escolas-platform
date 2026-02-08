
from sqlalchemy import Column, Integer, String, ForeignKey, Time, Date, Boolean, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class PontoProfessor(Base):
    __tablename__ = "ponto_professores"

    id = Column(Integer, primary_key=True, index=True)
    escola_id = Column(Integer, ForeignKey("escolas.id"))
    professor_id = Column(Integer, ForeignKey("usuarios.id"))
    data = Column(Date)
    presente = Column(Boolean, default=True)
    observacao = Column(String, nullable=True)
    
    professor = relationship("Usuario")
    # Auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class NotaBase(BaseModel):
    valor: float
    trimestre: str
    descricao: Optional[str] = "Prova"
    data_avaliacao: Optional[date] = None
    arquivo_url: Optional[str] = None  # <--- NOVO

class NotaCreate(NotaBase):
    aluno_id: int
    disciplina_id: int

class NotaResponse(NotaBase):
    id: int
    aluno_id: int
    disciplina_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
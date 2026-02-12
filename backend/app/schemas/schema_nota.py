from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class NotaBase(BaseModel):
    valor: float
    trimestre: str
    descricao: Optional[str] = "Prova"
    data_avaliacao: Optional[date] = None
    arquivo_url: Optional[str] = None

class NotaCreate(NotaBase):
    aluno_id: int
    disciplina_id: int
    # escola_id será injetado

class NotaResponse(NotaBase):
    id: int
    aluno_id: int
    aluno_nome: str               # enriquecido
    disciplina_id: int
    disciplina_nome: str          # enriquecido
    escola_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional

class PresencaItem(BaseModel):
    aluno_id: int
    status: str   # 'P', 'F', 'FJ'
    observacao: Optional[str] = None

class ChamadaDiaria(BaseModel):
    turma_id: int
    data: date
    lista: List[PresencaItem]
    # escola_id será injetado

class PresencaResponse(BaseModel):
    id: int
    data: date
    aluno_id: int
    aluno_nome: str
    turma_id: int
    turma_nome: str
    presente: bool
    justificado: bool
    observacao: Optional[str]
    status: Optional[str]
    escola_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
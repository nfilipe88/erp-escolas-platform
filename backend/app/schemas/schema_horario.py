from pydantic import BaseModel, ConfigDict
from datetime import time
from typing import Optional

class HorarioCreate(BaseModel):
    turma_id: int
    disciplina_id: Optional[int] = None
    professor_id: Optional[int] = None
    dia_semana: int
    hora_inicio: time
    hora_fim: time

class HorarioResponse(HorarioCreate):
    id: int
    escola_id: int
    disciplina_nome: Optional[str] = ""
    professor_nome: Optional[str] = ""

    model_config = ConfigDict(from_attributes=True)
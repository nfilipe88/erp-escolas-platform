from pydantic import BaseModel
from datetime import time, date
from typing import Optional

# --- HORÁRIO ---
class HorarioCreate(BaseModel):
    turma_id: int
    disciplina_id: int
    professor_id: int
    dia_semana: int
    hora_inicio: time
    hora_fim: time

class HorarioResponse(HorarioCreate):
    id: int
    disciplina_nome: Optional[str] = ""
    professor_nome: Optional[str] = ""
    
    class Config:
        from_attributes = True
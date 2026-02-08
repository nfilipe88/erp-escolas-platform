from pydantic import BaseModel
from datetime import time, date
from typing import Optional

# --- DIÁRIO (Para o professor enviar) ---
class DiarioCreate(BaseModel):
    horario_id: int
    resumo_aula: str

# --- PONTO PROFESSOR ---
class PontoProfessorCreate(BaseModel):
    professor_id: int
    data: date
    presente: bool
    
    class Config:
            from_attributes = True
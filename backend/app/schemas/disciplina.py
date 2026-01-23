from pydantic import BaseModel
from datetime import datetime
from typing import Optional  

class DisciplinaBase(BaseModel):
    nome: str
    codigo: str
    carga_horaria: int

class DisciplinaCreate(DisciplinaBase):
    turma_id: Optional[int] = None
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int
    created_at: datetime              # <--- Data de criação
    updated_at: Optional[datetime] = None # <--- Data de atualização (pode ser nula)
    
class Disciplina(DisciplinaBase):
    id: int
    turma_id: Optional[int] = None

    class Config:
        from_attributes = True
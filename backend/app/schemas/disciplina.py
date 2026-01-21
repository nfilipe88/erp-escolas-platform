from pydantic import BaseModel
from datetime import datetime
from typing import Optional  

class DisciplinaBase(BaseModel):
    nome: str
    turma_id: int

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int
    created_at: datetime              # <--- Data de criação
    updated_at: Optional[datetime] = None # <--- Data de atualização (pode ser nula)

    class Config:
        from_attributes = True
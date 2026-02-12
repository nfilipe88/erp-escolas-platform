from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional  

class DisciplinaBase(BaseModel):
    nome: str
    codigo: str
    carga_horaria: int

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int
    escola_id: int
    created_at: datetime              # <--- Data de criação
    updated_at: Optional[datetime] = None # <--- Data de atualização (pode ser nula)

    model_config = ConfigDict(from_attributes=True)
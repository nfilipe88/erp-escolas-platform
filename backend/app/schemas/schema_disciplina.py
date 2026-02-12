from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DisciplinaBase(BaseModel):
    nome: str
    codigo: str
    carga_horaria: int

class DisciplinaCreate(DisciplinaBase):
    escola_id: Optional[int] = None  # ← ADICIONADO (apenas superadmin envia)

class DisciplinaResponse(DisciplinaBase):
    id: int
    escola_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
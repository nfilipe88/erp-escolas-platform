from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TurmaBase(BaseModel):
    nome: str
    ano_letivo: str
    turno: Optional[str] = "Manhã"

class TurmaCreate(TurmaBase):
    escola_id: int

class TurmaResponse(TurmaBase):
    id: int
    escola_id: int
    created_at: datetime

    class Config:
        from_attributes = True
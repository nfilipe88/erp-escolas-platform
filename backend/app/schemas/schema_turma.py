from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TurmaBase(BaseModel):
    nome: str
    ano_letivo: str
    turno: Optional[str] = "Manhã"

class TurmaCreate(TurmaBase):
    escola_id: Optional[int] = None  # ← ADICIONADO (apenas superadmin envia)
    
class TurmaUpdate(BaseModel):
    nome: str
    ano_letivo: Optional[str] = None
    turno: Optional[str] = None

class TurmaResponse(TurmaBase):
    id: int
    escola_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class PontoProfessorCreate(BaseModel):
    data: date
    presente: bool
    observacao: Optional[str] = None
    # professor_id e escola_id serão injetados pelo backend

class PontoProfessorResponse(BaseModel):
    id: int
    professor_id: int
    professor_nome: str
    data: date
    presente: bool
    observacao: Optional[str]
    escola_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
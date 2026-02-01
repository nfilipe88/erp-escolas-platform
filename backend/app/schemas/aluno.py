from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class AlunoBase(BaseModel):
    nome: str
    bi: Optional[str] = None
    data_nascimento: Optional[date] = None
    turma_id: Optional[int] = None

class AlunoCreate(AlunoBase):
    escola_id: Optional[int] = None  # Será definido pelo backend
    ativo: bool = True  # Novo aluno é ativo por padrão
    
class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    bi: Optional[str] = None
    data_nascimento: Optional[date] = None
    turma_id: Optional[int] = None # Permitir atualização da turma
    ativo: Optional[bool] = None

class AlunoResponse(AlunoBase):
    id: int
    escola_id: int
    ativo: bool
    created_at: datetime

    class Config:
        from_attributes = True
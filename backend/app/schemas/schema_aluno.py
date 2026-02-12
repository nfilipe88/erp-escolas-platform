from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional

class AlunoBase(BaseModel):
    nome: str
    bi: Optional[str] = None
    data_nascimento: Optional[date] = None
    turma_id: Optional[int] = None

class AlunoCreate(AlunoBase):
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
    escola_nome: Optional[str] = None  # Para mostrar o nome da escola
    turma_nome: Optional[str] = None   # Para mostrar o nome da turma
    ativo: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
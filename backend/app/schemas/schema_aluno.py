from pydantic import BaseModel, ConfigDict, validator
from datetime import date, datetime
from typing import Optional
from app.core.validation import InputSanitizer

class AlunoBase(BaseModel):
    nome: str
    bi: Optional[str] = None
    data_nascimento: Optional[date] = None
    turma_id: Optional[int] = None
class AlunoCreate(BaseModel):
    nome: str
    bi: Optional[str] = None
    data_nascimento: Optional[date] = None
    turma_id: Optional[int] = None
    escola_id: Optional[int] = None
    ativo: bool = True
    
    @validator('nome')
    def validate_nome(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Nome deve ter no mínimo 3 caracteres')
        return InputSanitizer.sanitize_string(v, max_length=255)
    
    @validator('bi')
    def validate_bi(cls, v):
        if v:
            try:
                return InputSanitizer.sanitize_bi(v)
            except ValueError as e:
                raise ValueError(str(e))
        return v
    
    @validator('data_nascimento')
    def validate_data_nascimento(cls, v):
        if v:
            hoje = date.today()
            idade = (hoje - v).days // 365
            
            if idade < 3:
                raise ValueError('Aluno deve ter no mínimo 3 anos')
            if idade > 100:
                raise ValueError('Data de nascimento inválida')
        return v
    
    class Config:
        str_strip_whitespace = True
        anystr_strip_whitespace = True
    
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
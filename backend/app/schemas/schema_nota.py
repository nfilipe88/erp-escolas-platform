from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import date, datetime
from typing import Optional

class NotaBase(BaseModel):
    valor: float = Field(..., ge=0, le=20, description="Nota de 0 a 20")
    trimestre: str = Field(..., description="Ex: 1º Trimestre, 2º Trimestre")
    tipo_avaliacao: str = Field(..., description="Ex: MAC, Prova 1, Prova 2, Exame")
    descricao: Optional[str] = Field(None, description="Observação opcional")
    data_avaliacao: Optional[date] = None

    @field_validator('valor')
    def validar_nota(cls, v):
        # Arredondar para 1 casa decimal para evitar 15.333333
        return round(v, 1)

class NotaCreate(NotaBase):
    aluno_id: int
    disciplina_id: int
    turma_id: Optional[int] = None # Opcional, o Service pode inferir
    # escola_id será injetado

# Schema para ATUALIZAÇÃO
class NotaUpdate(BaseModel):
    valor: Optional[float] = Field(None, ge=0, le=20)
    descricao: Optional[str] = None

class NotaResponse(NotaBase):
    id: int
    aluno_id: int
    aluno_nome: str               # enriquecido
    disciplina_id: int
    disciplina_nome: str          # enriquecido
    escola_id: int
    escola_nome: str             # enriquecido

    model_config = ConfigDict(from_attributes=True)
    
# Schema para BOLETIM (Resumo)
class BoletimItem(BaseModel):
    disciplina: str
    nota_t1: Optional[float]
    nota_t2: Optional[float]
    nota_t3: Optional[float]
    media_final: Optional[float]
    resultado: str # Aprovado/Reprovado
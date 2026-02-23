from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional

# app/schemas/schema_presenca.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum

class StatusPresenca(str, Enum):
    PRESENTE = "Presente"
    AUSENTE = "Ausente"
    JUSTIFICADA = "Justificada"
    ATRASO = "Atraso"

# Base
class PresencaBase(BaseModel):
    data: date
    status: StatusPresenca
    observacao: Optional[str] = None

# Criação Individual
class PresencaCreate(PresencaBase):
    aluno_id: int
    disciplina_id: int
    turma_id: int

# Item para Chamada em Massa (Lista)
class ChamadaItem(BaseModel):
    aluno_id: int
    status: StatusPresenca
    observacao: Optional[str] = None

class RealizarChamadaRequest(BaseModel):
    turma_id: int
    disciplina_id: int
    data: date
    alunos: List[ChamadaItem]

# Atualização
class PresencaUpdate(BaseModel):
    status: Optional[StatusPresenca] = None
    observacao: Optional[str] = None


# Relatório de Frequência
class ResumoFrequencia(BaseModel):
    total_aulas: int
    total_presencas: int
    total_faltas: int
    percentual_frequencia: float

class PresencaItem(BaseModel):
    aluno_id: int
    status: str   # 'P', 'F', 'FJ'
    observacao: Optional[str] = None

class ChamadaDiaria(BaseModel):
    turma_id: int
    data: date
    lista: List[PresencaItem]
    # escola_id será injetado

class PresencaResponse(BaseModel):
    id: int
    data: date
    aluno_id: int
    aluno_nome: str
    turma_id: int
    turma_nome: str
    presente: bool
    justificado: bool
    observacao: Optional[str]
    status: Optional[str]
    disciplina_id: int
    disciplina_nome: str
    escola_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
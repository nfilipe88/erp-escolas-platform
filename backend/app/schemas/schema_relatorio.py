from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class ResumoFinanceiro(BaseModel):
    escola_id: int                      # contexto multi‑tenant
    total_arrecadado_mes: float
    total_atrasado_geral: float
    previsao_receita_mes: float

    model_config = ConfigDict(from_attributes=True)

class TransacaoFinanceira(BaseModel):
    id: int
    escola_id: int
    aluno_nome: str
    turma: str
    descricao: str
    valor: float
    data_pagamento: Optional[date]
    forma_pagamento: str

    model_config = ConfigDict(from_attributes=True)

class Devedor(BaseModel):
    escola_id: int
    aluno_id: int
    aluno_nome: str
    turma: str
    meses_atraso: int
    total_divida: float

    model_config = ConfigDict(from_attributes=True)
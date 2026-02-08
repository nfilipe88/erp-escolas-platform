# app/schemas/schema_relatorio.py
from pydantic import BaseModel
from datetime import date
from typing import Optional

class ResumoFinanceiro(BaseModel):
    total_arrecadado_mes: float
    total_atrasado_geral: float
    previsao_receita_mes: float

    class Config:
        from_attributes = True

class TransacaoFinanceira(BaseModel):
    id: int
    aluno_nome: str
    turma: str
    descricao: str
    valor: float
    data_pagamento: Optional[date]
    forma_pagamento: str

    class Config:
        from_attributes = True

class Devedor(BaseModel):
    aluno_id: int
    aluno_nome: str
    turma: str
    meses_atraso: int
    total_divida: float

    class Config:
        from_attributes = True
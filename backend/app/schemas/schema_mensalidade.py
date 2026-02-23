from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum

class StatusMensalidade(str, Enum):
    PENDENTE = "Pendente"
    PAGO = "Pago"
    ATRASADO = "Atrasado"
    CANCELADO = "Cancelado"

class FormaPagamento(str, Enum):
    NUMERARIO = "Numerário"
    TRANSFERENCIA = "Transferência"
    MULTICAIXA = "Multicaixa"
    DEPOSITO = "Depósito"

# Base
class MensalidadeBase(BaseModel):
    mes: int = Field(..., ge=1, le=12, description="Mês de referência (1-12)")
    ano: int = Field(..., ge=2000, le=2100)
    valor_base: float = Field(..., gt=0)
    data_vencimento: date
    estado: str = StatusMensalidade.PENDENTE.value
    descricao: str # Ex: "Mensalidade - Fevereiro 2025"

# Para criar uma dívida (Gerado pelo sistema)
class MensalidadeCreate(MensalidadeBase):
    aluno_id: int

# Para registrar o pagamento (O que muda quando o pai paga)
class MensalidadePagar(BaseModel):
    data_pagamento: date
    forma_pagamento: str # "TPA", "Numerário", "Transferência"
    
# Para o ato de pagar
class RealizarPagamento(BaseModel):
    forma_pagamento: FormaPagamento
    observacao: Optional[str] = None
    multa: float = 0.0
    desconto: float = 0.0

class MensalidadeResponse(MensalidadeBase):
    id: int
    aluno_id: int
    aluno_nome: str                # enriquecido
    escola_id: int
    data_emissao: date
    data_pagamento: Optional[date] = None
    forma_pagamento: Optional[str] = None
    criado_por_id: int
    criado_por_nome: str          # enriquecido
    pago_por_id: Optional[int] = None
    pago_por_nome: Optional[str] = None  # enriquecido
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    
# Utilitário para geração em massa
class GerarCarnetRequest(BaseModel):
    aluno_id: int
    ano_letivo: int
    valor_mensal: float
    dia_vencimento: int # Default dia 10 de cada mês
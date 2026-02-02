from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class MensalidadeBase(BaseModel):
    mes: str
    ano: int
    valor_base: float
    estado: str = "Pendente" # Pendente, Pago, Atrasado, Cancelado
    descricao: str # Ex: "Mensalidade - Fevereiro 2025"
    data_vencimento: date

# Para criar uma dívida (Gerado pelo sistema)
class MensalidadeCreate(MensalidadeBase):
    aluno_id: int
    escola_id: int # Segurança SaaS
    criado_por_id: int # ID do funcionário que gerou o carnet

# Para registrar o pagamento (O que muda quando o pai paga)
class MensalidadePagar(BaseModel):
    data_pagamento: date
    forma_pagamento: str # "TPA", "Numerário", "Transferência"
    # IMPORTANTE: Tornar este campo opcional na entrada, pois vamos preenchê-lo no backend
    pago_por_id: Optional[int] = Field(default=None, exclude=True)

class MensalidadeResponse(MensalidadeBase):
    id: int
    aluno_id: int
    escola_id: int
    data_emissao: date
    data_pagamento: Optional[date]
    forma_pagamento: Optional[str]
    criado_por_id: int
    pago_por_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
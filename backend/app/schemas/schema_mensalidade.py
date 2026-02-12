from pydantic import BaseModel, ConfigDict, Field
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

# Para registrar o pagamento (O que muda quando o pai paga)
class MensalidadePagar(BaseModel):
    data_pagamento: date
    forma_pagamento: str # "TPA", "Numerário", "Transferência"

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
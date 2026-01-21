from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class MensalidadeBase(BaseModel):
    mes: str
    ano: int
    valor_base: float
    estado: str = "Pendente"

# Para criar uma dívida (geralmente gerado automaticamente)
class MensalidadeCreate(MensalidadeBase):
    aluno_id: int

# Para registrar o pagamento (O que muda quando o pai paga)
class MensalidadePagar(BaseModel):
    data_pagamento: date
    forma_pagamento: str # "TPA", "Dinheiro"

class MensalidadeResponse(MensalidadeBase):
    id: int
    aluno_id: int
    data_pagamento: Optional[date]
    forma_pagamento: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
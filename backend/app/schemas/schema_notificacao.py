from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NotificacaoBase(BaseModel):
    titulo: str
    mensagem: str

class NotificacaoCreate(NotificacaoBase):
    usuario_id: int

class NotificacaoResponse(NotificacaoBase):
    id: int
    lida: bool
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)
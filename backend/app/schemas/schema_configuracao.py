# app/schemas/configuracao.py
from pydantic import BaseModel, ConfigDict, Field

class ConfiguracaoBase(BaseModel):
    valor_mensalidade_padrao: float = Field(..., gt=0, description="O valor base em Kz")
    dia_vencimento: int = Field(..., ge=1, le=28, description="Dia do mês (1 a 28)")
    multa_atraso_percentual: float = Field(..., ge=0, description="Ex: 5.0 para 5%")
    desconto_pagamento_anual: float = Field(..., ge=0, description="Ex: 10.0 para 10%")
    mes_inicio_cobranca: int = Field(..., ge=1, le=12)
    mes_fim_cobranca: int = Field(..., ge=1, le=12)
    bloquear_boletim_devedor: bool
    nota_minima_aprovacao: float = Field(..., ge=0, le=20)

# O que o Frontend envia para atualizar
class ConfiguracaoUpdate(ConfiguracaoBase):
    pass

# O que o Backend devolve
class ConfiguracaoResponse(ConfiguracaoBase):
    id: int
    escola_id: int

    model_config = ConfigDict(from_attributes=True)
# app/cruds/crud_configuracao.py
from sqlalchemy.orm import Session
from app.models import configuracao as models
from app.schemas import schema_configuracao

def get_config_by_escola(db: Session, escola_id: int):
    return db.query(models.Configuracao).filter(models.Configuracao.escola_id == escola_id).first()

def update_config(db: Session, escola_id: int, dados: schema_configuracao.ConfiguracaoUpdate):
    db_config = get_config_by_escola(db, escola_id)
    if not db_config:
        db_config = models.Configuracao(escola_id=escola_id)
        db.add(db_config)

    db_config.valor_mensalidade_padrao = dados.valor_mensalidade_padrao
    db_config.dia_vencimento = dados.dia_vencimento
    db_config.multa_atraso_percentual = dados.multa_atraso_percentual
    db_config.desconto_pagamento_anual = dados.desconto_pagamento_anual
    db_config.mes_inicio_cobranca = dados.mes_inicio_cobranca
    db_config.mes_fim_cobranca = dados.mes_fim_cobranca
    db_config.bloquear_boletim_devedor = dados.bloquear_boletim_devedor
    db_config.nota_minima_aprovacao = dados.nota_minima_aprovacao

    db.commit()
    db.refresh(db_config)
    return db_config
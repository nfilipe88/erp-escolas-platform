# app/cruds/crud_mensalidade.py
from sqlalchemy import extract
from sqlalchemy.orm import Session
from app.models import mensalidade as models
from app.models import aluno as models_aluno
from app.models import configuracao as models_config
from app.schemas import schema_mensalidade
from datetime import date
from fastapi import HTTPException
from app.cruds import crud_configuracao
from typing import Optional

from app.schemas import schema_mensalidade as schemas

MESES_NOME = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

def gerar_carnet_aluno(db: Session, aluno_id: int, ano_letivo: int, current_user_id: int):
    carnet_existente = db.query(models.Mensalidade).filter(
        models.Mensalidade.aluno_id == aluno_id,
        models.Mensalidade.ano == ano_letivo
    ).first()

    if carnet_existente:
        raise HTTPException(
            status_code=400,
            detail=f"O Carnet de {ano_letivo} já foi gerado. Não é possível gerar novamente."
        )

    aluno = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    config = db.query(models_config.Configuracao).filter(
        models_config.Configuracao.escola_id == aluno.escola_id
    ).first()

    dia_venc = config.dia_vencimento if config else 10
    mes_inicio = config.mes_inicio_cobranca if config else 2
    mes_fim = config.mes_fim_cobranca if config else 12
    valor_padrao = config.valor_mensalidade_padrao if config else 35000.0

    meses_a_gerar = []
    if mes_inicio <= mes_fim:
        for m in range(mes_inicio, mes_fim + 1):
            meses_a_gerar.append((m, ano_letivo))
    else:
        for m in range(mes_inicio, 13):
            meses_a_gerar.append((m, ano_letivo))
        for m in range(1, mes_fim + 1):
            meses_a_gerar.append((m, ano_letivo + 1))

    for mes_num, ano_real in meses_a_gerar:
        nome_mes = MESES_NOME[mes_num]
        try:
            data_vencimento_real = date(ano_real, mes_num, dia_venc)
        except ValueError:
            data_vencimento_real = date(ano_real, mes_num, 28)

        nova = models.Mensalidade(
            aluno_id=aluno_id,
            escola_id=aluno.escola_id,
            criado_por_id=current_user_id,
            descricao=f"Mensalidade - {nome_mes} {ano_real}",
            mes=nome_mes,
            ano=ano_real,
            valor_base=valor_padrao,
            data_vencimento=data_vencimento_real,
            estado="Pendente"
        )
        db.add(nova)

    db.commit()
    return get_mensalidades_aluno(db, aluno_id, escola_id=aluno.escola_id)

def get_mensalidades_aluno(db: Session, aluno_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Mensalidade).filter(models.Mensalidade.aluno_id == aluno_id)
    if escola_id:
        query = query.filter(models.Mensalidade.escola_id == escola_id)
    return query.order_by(models.Mensalidade.data_vencimento).all()

def get_mensalidade(db: Session, mensalidade_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Mensalidade).filter(models.Mensalidade.id == mensalidade_id)
    if escola_id:
        query = query.filter(models.Mensalidade.escola_id == escola_id)
    return query.first()

def pagar_mensalidade(db: Session, mensalidade_id: int,
                      dados_pagamento: schema_mensalidade.MensalidadePagar,
                      pago_por_id: int, escola_id: int):
    db_mensalidade = db.query(models.Mensalidade).filter(
        models.Mensalidade.id == mensalidade_id,
        models.Mensalidade.escola_id == escola_id
    ).first()

    if db_mensalidade:
        config = crud_configuracao.get_config_by_escola(db, db_mensalidade.escola_id)
        multa_percentual = config.multa_atraso_percentual if config else 0.0

        hoje = date.today()
        if hoje > db_mensalidade.data_vencimento and multa_percentual > 0:
            valor_multa = db_mensalidade.valor_base * (multa_percentual / 100)
            db_mensalidade.valor_base += valor_multa

        db_mensalidade.estado = "Pago"
        db_mensalidade.data_pagamento = dados_pagamento.data_pagamento
        db_mensalidade.forma_pagamento = dados_pagamento.forma_pagamento
        db_mensalidade.pago_por_id = pago_por_id

        db.commit()
        db.refresh(db_mensalidade)

    return db_mensalidade

# --- FUNÇÃO EM FALTA 1: CRIAR MENSALIDADE ---
def create_mensalidade(db: Session, mensalidade: schemas.MensalidadeCreate, escola_id: int):
    # Verifica duplicados (mesmo aluno, mesmo mês/ano)
    ano_atual = date.today().year
    mes_atual = date.today().month # Simplificação, idealmente vem do payload ou data_vencimento
    
    # Se a mensalidade tiver data de vencimento, usamos para extrair mês/ano
    if mensalidade.data_vencimento:
        mes_atual = mensalidade.data_vencimento.month
        ano_atual = mensalidade.data_vencimento.year

    existente = db.query(models.Mensalidade).filter(
        models.Mensalidade.aluno_id == mensalidade.aluno_id,
        extract('month', models.Mensalidade.data_vencimento) == mes_atual,
        extract('year', models.Mensalidade.data_vencimento) == ano_atual
    ).first()

    if existente:
        return None # Ou levantar exceção

    # Criação do objeto
    db_mensalidade = models.Mensalidade(
        escola_id=escola_id,
        aluno_id=mensalidade.aluno_id,
        valor_base=mensalidade.valor_base,
        data_vencimento=mensalidade.data_vencimento,
        descricao=mensalidade.descricao or f"Mensalidade {mes_atual}/{ano_atual}",
        estado="Pendente"
    )
    db.add(db_mensalidade)
    db.commit()
    db.refresh(db_mensalidade)
    return db_mensalidade

# --- FUNÇÃO EM FALTA 2: REGISTAR PAGAMENTO ---
def registar_pagamento(db: Session, mensalidade_id: int, forma_pagamento: str):
    mensalidade = db.query(models.Mensalidade).filter(models.Mensalidade.id == mensalidade_id).first()
    
    if not mensalidade:
        return None
    
    if mensalidade.estado == "Pago":
        return mensalidade # Já está pago, retorna sem erro

    # Atualiza campos
    mensalidade.estado = "Pago" # type: ignore (Pylance reclama de atribuição a Column)
    mensalidade.data_pagamento = date.today() # type: ignore
    mensalidade.forma_pagamento = forma_pagamento # type: ignore
    
    db.commit()
    db.refresh(mensalidade)
    return mensalidade

# Função auxiliar para evitar erros de tipagem no extract
def get_config_by_escola(db: Session, escola_id: int):
    # Implementar lógica real se tiveres tabela de Configuração Financeira
    # Por agora retorna um dicionário padrão
    return {"multa_percentual": 10, "dia_vencimento": 5}
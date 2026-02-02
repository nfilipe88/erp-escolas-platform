# app/cruds/crud_mensalidade.py

from sqlalchemy.orm import Session
from app.models import mensalidade as models
from app.models import aluno as models_aluno
from app.models import escola as models_escola
from app.models import configuracao as models_config
from app.schemas import schema_mensalidade
from datetime import date
from fastapi import HTTPException
from app.cruds import crud_configuracao
from datetime import date

# Mapeamento útil de Número do Mês para Nome
MESES_NOME = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
# 1. Criar mensalidade
def gerar_carnet_aluno(db: Session, aluno_id: int, ano_letivo: int, current_user_id: int):
    """
    Gera o carnet financeiro.
    BLOQUEIA se já existirem mensalidades registadas para esse ano.
    """
    
    # 1. VERIFICAÇÃO DE SEGURANÇA (REGRA DE OURO) 🔒
    # Verifica se existe pelo menos UMA mensalidade para este aluno neste ano.
    carnet_existente = db.query(models.Mensalidade).filter(
        models.Mensalidade.aluno_id == aluno_id,
        models.Mensalidade.ano == ano_letivo
    ).first()

    if carnet_existente:
        # Se encontrou algo, para imediatamente e lança erro.
        raise HTTPException(
            status_code=400, 
            detail=f"O Carnet de {ano_letivo} já foi gerado. Não é possível gerar novamente."
        )

    # 2. Buscar o Aluno
    aluno = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")

    # 3. Buscar Configurações
    config = db.query(models_config.Configuracao).filter(models_config.Configuracao.escola_id == aluno.escola_id).first()
    
    dia_venc = config.dia_vencimento if config else 10
    mes_inicio = config.mes_inicio_cobranca if config else 2
    mes_fim = config.mes_fim_cobranca if config else 12
    valor_padrao = config.valor_mensalidade_padrao if config else 35000.0

    # 4. Calcular Meses
    meses_a_gerar = []
    if mes_inicio <= mes_fim:
        for m in range(mes_inicio, mes_fim + 1):
            meses_a_gerar.append((m, ano_letivo))
    else:
        for m in range(mes_inicio, 13):
            meses_a_gerar.append((m, ano_letivo))
        for m in range(1, mes_fim + 1):
            meses_a_gerar.append((m, ano_letivo + 1))

    # 5. Gerar
    for mes_num, ano_real in meses_a_gerar:
        nome_mes = MESES_NOME[mes_num]
        
        try:
            data_vencimento_real = date(ano_real, mes_num, dia_venc)
        except ValueError:
            data_vencimento_real = date(ano_real, mes_num, 28)

        nova_mensalidade = models.Mensalidade(
            aluno_id=aluno_id,
            escola_id=aluno.escola_id,
            criado_por_id=current_user_id,
            descricao=f"Mensalidade - {nome_mes} {ano_real}",
            mes=nome_mes,
            ano=ano_real, # Importante: guarda o ano real da mensalidade (pode ser 2026 num carnet de 2025/26)
            valor_base=valor_padrao,
            data_vencimento=data_vencimento_real,
            estado="Pendente"
        )
        db.add(nova_mensalidade)
    
    db.commit()
    return get_mensalidades_aluno(db, aluno_id)

# 2. Ler mensalidades do aluno (Extrato)
def get_mensalidades_aluno(db: Session, aluno_id: int):
    return db.query(models.Mensalidade).filter(models.Mensalidade.aluno_id == aluno_id).order_by(models.Mensalidade.data_vencimento).all()

# 3. Pagar uma mensalidade (COM LÓGICA DE MULTA AUTOMÁTICA)
def pagar_mensalidade(db: Session, mensalidade_id: int, dados_pagamento: schema_mensalidade.MensalidadePagar):
    db_mensalidade = db.query(models.Mensalidade).filter(models.Mensalidade.id == mensalidade_id).first()
    
    if db_mensalidade:
        # 1. Buscar as configurações financeiras da escola
        config = crud_configuracao.get_config_by_escola(db, db_mensalidade.escola_id) # type: ignore
        
        # Pega na percentagem de multa (se não existir config, assume 0%)
        multa_percentual = config.multa_atraso_percentual if config else 0.0

        # 2. LÓGICA DA MULTA (A Matemática do ERP)
        hoje = date.today()
        
        # Só aplica multa se estiver atrasado E se a multa for maior que 0
        if hoje > db_mensalidade.data_vencimento and multa_percentual > 0: # type: ignore
            # Cálculo: Valor Base * (Percentagem / 100)
            valor_multa = db_mensalidade.valor_base * (multa_percentual / 100)
            valor_total = db_mensalidade.valor_base + valor_multa
            
            # Atualiza o valor para o novo total com multa
            db_mensalidade.valor_base = valor_total #type: ignore
            # (Num ERP avançado criaríamos um campo 'multa_aplicada', mas assim já funciona perfeitamente para o Recibo)

        # 3. Efetivar o Pagamento
        db_mensalidade.estado = "Pago" # type: ignore
        db_mensalidade.data_pagamento = dados_pagamento.data_pagamento # type: ignore
        db_mensalidade.forma_pagamento = dados_pagamento.forma_pagamento # type: ignore
        db_mensalidade.pago_por_id = dados_pagamento.pago_por_id # Auditoria# type: ignore
        
        db.commit()
        db.refresh(db_mensalidade)
        
    return db_mensalidade

def get_mensalidade(db: Session, mensalidade_id: int):
    return db.query(models.Mensalidade).filter(models.Mensalidade.id == mensalidade_id).first()
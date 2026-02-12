# app/cruds/crud_financeiro_relatorio.py
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from app.models import mensalidade as models_fin
from app.models import aluno as models_aluno
from app.models import turma as models_turma
from datetime import date

def get_resumo_mes(db: Session, escola_id: int):
    hoje = date.today()

    def safe_sum(query):
        val = query.scalar()
        return float(val) if val else 0.0

    receita = safe_sum(db.query(func.sum(models_fin.Mensalidade.valor_base)).filter(
        models_fin.Mensalidade.escola_id == escola_id,
        models_fin.Mensalidade.estado == 'Pago',
        extract('month', models_fin.Mensalidade.data_pagamento) == hoje.month,
        extract('year', models_fin.Mensalidade.data_pagamento) == hoje.year
    ))

    atrasado = safe_sum(db.query(func.sum(models_fin.Mensalidade.valor_base)).filter(
        models_fin.Mensalidade.escola_id == escola_id,
        models_fin.Mensalidade.estado == 'Pendente',
        models_fin.Mensalidade.data_vencimento < hoje
    ))

    previsao = safe_sum(db.query(func.sum(models_fin.Mensalidade.valor_base)).filter(
        models_fin.Mensalidade.escola_id == escola_id,
        extract('month', models_fin.Mensalidade.data_vencimento) == hoje.month,
        extract('year', models_fin.Mensalidade.data_vencimento) == hoje.year
    ))

    return {
        "total_arrecadado_mes": receita,
        "total_atrasado_geral": atrasado,
        "previsao_receita_mes": previsao
    }

def get_fluxo_caixa(db: Session, escola_id: int, limit: int = 50):
    results = db.query(models_fin.Mensalidade, models_aluno.Aluno, models_turma.Turma)\
        .join(models_aluno.Aluno, models_fin.Mensalidade.aluno_id == models_aluno.Aluno.id)\
        .join(models_turma.Turma, models_aluno.Aluno.turma_id == models_turma.Turma.id)\
        .filter(
            models_fin.Mensalidade.escola_id == escola_id,
            models_fin.Mensalidade.estado == 'Pago'
        )\
        .order_by(desc(models_fin.Mensalidade.data_pagamento))\
        .limit(limit).all()

    lista = []
    for mensalidade, aluno, turma in results:
        lista.append({
            "id": mensalidade.id,
            "aluno_nome": aluno.nome,
            "turma": turma.nome,
            "descricao": mensalidade.descricao,
            "valor": float(mensalidade.valor_base or 0),
            "data_pagamento": mensalidade.data_pagamento,
            "forma_pagamento": mensalidade.forma_pagamento or "Caixa"
        })
    return lista

def get_top_devedores(db: Session, escola_id: int):
    return db.query(models_aluno.Aluno)\
        .join(models_fin.Mensalidade)\
        .filter(
            models_aluno.Aluno.escola_id == escola_id,
            models_fin.Mensalidade.estado == "Pendente"
        )\
        .limit(10).all()
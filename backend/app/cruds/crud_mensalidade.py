from sqlalchemy.orm import Session
from app.models import mensalidade as models
from app.schemas import mensalidade as schemas
from datetime import date

# 1. Gerar Carnet Anual (Cria meses Pendentes)
def gerar_carnet_aluno(db: Session, aluno_id: int, ano: int, valor: float):
    meses = ["Fevereiro", "Março", "Abril", "Maio", "Junho", 
             "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    lista_criada = []
    for mes in meses:
        # Verifica se já existe para não duplicar
        existe = db.query(models.Mensalidade).filter(
            models.Mensalidade.aluno_id == aluno_id,
            models.Mensalidade.mes == mes,
            models.Mensalidade.ano == ano
        ).first()

        if not existe:
            db_mensalidade = models.Mensalidade(
                aluno_id=aluno_id,
                mes=mes,
                ano=ano,
                valor_base=valor,
                estado="Pendente"
            )
            db.add(db_mensalidade)
            lista_criada.append(db_mensalidade)
    
    db.commit()
    return lista_criada

# 2. Ler mensalidades do aluno
def get_mensalidades_aluno(db: Session, aluno_id: int):
    return db.query(models.Mensalidade).filter(models.Mensalidade.aluno_id == aluno_id).all()

# 3. Pagar uma mensalidade
def pagar_mensalidade(db: Session, mensalidade_id: int, dados_pagamento: schemas.MensalidadePagar):
    db_mensalidade = db.query(models.Mensalidade).filter(models.Mensalidade.id == mensalidade_id).first()
    if db_mensalidade:
        db_mensalidade.estado = "Pago" # type: ignore
        db_mensalidade.data_pagamento = dados_pagamento.data_pagamento # type: ignore
        db_mensalidade.forma_pagamento = dados_pagamento.forma_pagamento # type: ignore
        db.commit()
        db.refresh(db_mensalidade)
    return db_mensalidade

def get_mensalidade_by_id(db: Session, id: int):
    # O SQLAlchemy carrega automaticamente o Aluno por causa do relationship
    return db.query(models.Mensalidade).filter(models.Mensalidade.id == id).first()
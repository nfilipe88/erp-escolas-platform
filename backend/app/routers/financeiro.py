from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_mensalidade as schemas_fin
from app.schemas import schema_relatorio
from app.cruds import crud_mensalidade, crud_financeiro_relatorio
from app.models import usuario as models_user

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

# --- Gestão de Mensalidades (Carnets) ---

@router.post("/gerar-carnet/{aluno_id}") # Ajustei a rota para ser mais RESTful, mas podes manter a original se preferires
def gerar_mensalidades(
    aluno_id: int, 
    ano: int, # Query param: ?ano=2025
    db: Session = Depends(get_db), 
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.gerar_carnet_aluno(
        db=db, 
        aluno_id=aluno_id, 
        ano_letivo=ano, 
        current_user_id=current_user.id
    )

@router.get("/aluno/{aluno_id}", response_model=List[schemas_fin.MensalidadeResponse])
def ver_financeiro_aluno(
    aluno_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Nota: Mudei ligeiramente a rota para /financeiro/aluno/{id} para agrupar tudo no prefixo /financeiro
    # Se preferires manter /alunos/{id}/financeiro, terás de criar este endpoint no routers/alunos.py
    return crud_mensalidade.get_mensalidades_aluno(db=db, aluno_id=aluno_id)

@router.put("/{mensalidade_id}/pagar", response_model=schemas_fin.MensalidadePagar)
def pagar_mensalidade(
    mensalidade_id: int, 
    dados_pagamento: schemas_fin.MensalidadePagar, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    dados_pagamento.pago_por_id = current_user.id
    return crud_mensalidade.pagar_mensalidade(db, mensalidade_id, dados_pagamento)

@router.get("/{mensalidade_id}", response_model=schemas_fin.MensalidadeResponse)
def get_recibo(
    mensalidade_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.get_mensalidade(db=db, mensalidade_id=mensalidade_id)

# ==========================================
# --- RELATÓRIOS FINANCEIROS ---
# ==========================================
@router.get("/relatorios/resumo", response_model=schema_relatorio.ResumoFinanceiro)
def financeiro_resumo(db: Session = Depends(get_db),
                      current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_financeiro_relatorio.get_resumo_mes(db, current_user.escola_id)

@router.get("/relatorios/fluxo", response_model=List[schema_relatorio.TransacaoFinanceira])
def financeiro_fluxo(db: Session = Depends(get_db),
                     current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_financeiro_relatorio.get_fluxo_caixa(db, current_user.escola_id)

@router.get("/relatorios/devedores", response_model=List[schema_relatorio.Devedor])
def financeiro_devedores(db: Session = Depends(get_db),
                         current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_financeiro_relatorio.get_top_devedores(db, current_user.escola_id)
# ==========================================
# FIM DO MÓDULO DE RELATÓRIOS FINANCEIROS
# ==========================================
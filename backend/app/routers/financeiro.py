from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_mensalidade as schemas_fin
from app.schemas import schema_relatorio
from app.cruds import crud_mensalidade, crud_financeiro_relatorio, crud_aluno
from app.models import usuario as models_user
from app.security_decorators import require_escola_id, verify_resource_ownership, admin_or_superadmin_required

router = APIRouter(prefix="/financeiro", tags=["Financeiro"])

@router.post("/gerar-carnet/{aluno_id}")
def gerar_mensalidades(
    aluno_id: int,
    ano: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    aluno = crud_aluno.get_aluno(db, aluno_id, escola_id=escola_id)
    if not aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    verify_resource_ownership(aluno.escola_id, current_user, "aluno")  # type: ignore[arg-type]
    return crud_mensalidade.gerar_carnet_aluno(
        db=db,
        aluno_id=aluno_id,
        ano_letivo=ano,
        current_user_id=current_user.id  # type: ignore[arg-type]
    )

@router.get("/aluno/{aluno_id}", response_model=List[schemas_fin.MensalidadeResponse])
def ver_financeiro_aluno(
    aluno_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    aluno = crud_aluno.get_aluno(db, aluno_id, escola_id=escola_id)
    if not aluno:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")
    return crud_mensalidade.get_mensalidades_aluno(db, aluno_id, escola_id=escola_id)

@router.put("/{mensalidade_id}/pagar", response_model=schemas_fin.MensalidadeResponse)
def pagar_mensalidade(
    mensalidade_id: int,
    dados_pagamento: schemas_fin.MensalidadePagar,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    mensalidade = crud_mensalidade.get_mensalidade(db, mensalidade_id, escola_id=escola_id)
    if not mensalidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensalidade não encontrada")
    verify_resource_ownership(mensalidade.escola_id, current_user, "mensalidade")  # type: ignore[arg-type]
    return crud_mensalidade.pagar_mensalidade(
        db, mensalidade_id, dados_pagamento,
        pago_por_id=current_user.id,  # type: ignore[arg-type]
        escola_id=escola_id
    )

@router.get("/{mensalidade_id}", response_model=schemas_fin.MensalidadeResponse)
def get_recibo(
    mensalidade_id: int,
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    mensalidade = crud_mensalidade.get_mensalidade(db, mensalidade_id, escola_id=escola_id)
    if not mensalidade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mensalidade não encontrada")
    return mensalidade

# --- RELATÓRIOS FINANCEIROS ---
@router.get("/relatorios/resumo", response_model=schema_relatorio.ResumoFinanceiro)
def financeiro_resumo(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    return crud_financeiro_relatorio.get_resumo_mes(db, escola_id)

@router.get("/relatorios/fluxo", response_model=List[schema_relatorio.TransacaoFinanceira])
def financeiro_fluxo(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    return crud_financeiro_relatorio.get_fluxo_caixa(db, escola_id)

@router.get("/relatorios/devedores", response_model=List[schema_relatorio.Devedor])
def financeiro_devedores(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    return crud_financeiro_relatorio.get_top_devedores(db, escola_id)
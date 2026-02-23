from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_mensalidade as schemas_fin
from app.schemas import schema_relatorio
from app.cruds import crud_mensalidade, crud_financeiro_relatorio, crud_aluno
from app.models import usuario as models_user
from app.security_decorators import require_escola_id, verify_resource_ownership, admin_or_superadmin_required

# app/routers/financeiro.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import schema_mensalidade
from app.services.financeiro_service import FinanceiroService
from app.security import get_current_user
from app.models.usuario import Usuario

router = APIRouter()

def get_financeiro_service(db: Session = Depends(get_db)) -> FinanceiroService:
    return FinanceiroService(db)

@router.post("/gerar-carnet", response_model=List[schema_mensalidade.MensalidadeResponse])
def gerar_carnet(
    dados: schema_mensalidade.GerarCarnetRequest,
    service: FinanceiroService = Depends(get_financeiro_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Gera todas as mensalidades do ano para um aluno"""
    return service.gerar_carnet_anual(dados, current_user)

@router.post("/{mensalidade_id}/pagar", response_model=schema_mensalidade.MensalidadeResponse)
def registrar_pagamento(
    mensalidade_id: int,
    pagamento: schema_mensalidade.RealizarPagamento,
    service: FinanceiroService = Depends(get_financeiro_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra o pagamento de uma mensalidade"""
    return service.registrar_pagamento(mensalidade_id, pagamento, current_user)

@router.get("/aluno/{aluno_id}", response_model=List[schema_mensalidade.MensalidadeResponse])
def listar_financeiro_aluno(
    aluno_id: int,
    service: FinanceiroService = Depends(get_financeiro_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Extrato financeiro do aluno"""
    return service.listar_por_aluno(aluno_id, current_user)

@router.delete("/{mensalidade_id}/cancelar")
def cancelar_mensalidade(
    mensalidade_id: int,
    motivo: str,
    service: FinanceiroService = Depends(get_financeiro_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Cancela uma cobrança indevida"""
    service.cancelar_mensalidade(mensalidade_id, motivo, current_user)
    return {"message": "Mensalidade cancelada com sucesso"}


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
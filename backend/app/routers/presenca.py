from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_presenca, schema_diario
from app.cruds import crud_presenca, crud_ponto, crud_turma, crud_horario
from app.models import usuario as models_user
from app.models import diario as models_diario
from app.models import horario as models_horario
from app.security_decorators import (
    require_escola_id,
    verify_resource_ownership,
    get_current_escola_id,
    admin_or_superadmin_required
)

router = APIRouter(prefix="/presencas", tags=["Presença e Ponto"])

# --- Chamada de Alunos ---
@router.post("/chamada", response_model=List[schema_presenca.PresencaResponse])
def realizar_chamada(
    dados: schema_presenca.ChamadaDiaria,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    # Permissão: admin, secretaria ou professor da turma (simplificado)
    if current_user.perfil not in ['admin', 'secretaria', 'superadmin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão negada para realizar chamada.")
    turma = crud_turma.get_turma(db, dados.turma_id, escola_id=escola_id)
    if not turma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Turma não encontrada")
    verify_resource_ownership(turma.escola_id, current_user, "turma")
    return crud_presenca.registrar_chamada(db, dados, escola_id)

@router.get("/chamada/{turma_id}/{data}")
def consultar_chamada(
    turma_id: int,
    data: str,
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    presencas = crud_presenca.get_presencas_dia(db, turma_id, data_obj, escola_id=escola_id)
    return presencas

# --- Diário de Aula (Professor) ---
@router.post("/diario")
def finalizar_aula(
    dados: schema_diario.DiarioCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user),
    escola_id: int = Depends(require_escola_id)
):
    if current_user.perfil != "professor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Apenas professores podem lançar diário.")
    horario = db.query(models_horario.Horario).filter(
        models_horario.Horario.id == dados.horario_id,
        models_horario.Horario.escola_id == escola_id,
        models_horario.Horario.professor_id == current_user.id
    ).first()
    if not horario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Horário não encontrado ou não pertence ao professor")
    novo_diario = models_diario.Diario(
        escola_id=escola_id,
        horario_id=dados.horario_id,
        professor_id=current_user.id,
        data=datetime.now().date(),
        resumo_aula=dados.resumo_aula,
        fechado=True
    )
    db.add(novo_diario)
    db.commit()
    return {"msg": "Diário enviado à secretaria com sucesso!"}

# --- Ponto dos Professores ---
@router.get("/ponto-professores/{data}")
def ver_ponto_professores(
    data: str,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    return crud_ponto.get_ponto_dia(db, escola_id, data_obj)

@router.post("/ponto-professores")
def registrar_ponto_professores(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required),
    escola_id: int = Depends(require_escola_id)
):
    data_obj = datetime.strptime(payload['data'], "%Y-%m-%d").date()
    return crud_ponto.salvar_ponto(db, escola_id, payload['lista'], data_obj)
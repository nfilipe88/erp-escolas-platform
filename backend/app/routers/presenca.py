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

# app/routers/presenca.py
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import schema_presenca
from app.services.presenca_service import PresencaService
from app.security import get_current_user
from app.models.usuario import Usuario

router = APIRouter()

def get_presenca_service(db: Session = Depends(get_db)) -> PresencaService:
    return PresencaService(db)

@router.post("/chamada", status_code=status.HTTP_200_OK)
def realizar_chamada(
    dados: schema_presenca.RealizarChamadaRequest,
    service: PresencaService = Depends(get_presenca_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Endpoint principal para professores.
    Recebe a lista de alunos e status para um dia/disciplina.
    """
    return service.realizar_chamada(dados, current_user)

@router.get("/turma/{turma_id}", response_model=List[schema_presenca.PresencaResponse])
def ver_chamada_dia(
    turma_id: int,
    disciplina_id: int,
    data: date,
    service: PresencaService = Depends(get_presenca_service),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Vê quem estava presente num dia específico.
    Ex: /presenca/turma/1?disciplina_id=5&data=2023-10-20
    """
    return service.listar_por_turma_data(turma_id, disciplina_id, data, current_user)

@router.put("/{presenca_id}", response_model=schema_presenca.PresencaResponse)
def corrigir_presenca(
    presenca_id: int,
    dados: schema_presenca.PresencaUpdate,
    service: PresencaService = Depends(get_presenca_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Corrige um erro de lançamento (ex: mudar falta para justificada)"""
    return service.atualizar_presenca(presenca_id, dados, current_user)

@router.get("/aluno/{aluno_id}/estatistica")
def estatistica_frequencia(
    aluno_id: int,
    disciplina_id: int,
    service: PresencaService = Depends(get_presenca_service),
    current_user: Usuario = Depends(get_current_user)
):
    """Retorna % de frequência para exibir no boletim ou dashboard"""
    return service.calcular_frequencia_aluno(aluno_id, disciplina_id, current_user)


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
    if current_user.perfil != "professor":  # type: ignore[comparison-overlap]
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
        professor_id=current_user.id,  # type: ignore[arg-type]
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
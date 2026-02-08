from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_presenca, schema_diario
from app.cruds import crud_presenca, crud_ponto
from app.models import usuario as models_user
from app.models import diario as models_diario

router = APIRouter(tags=["Presença e Ponto"])

# --- Chamada de Alunos ---

@router.post("/presencas/")
def realizar_chamada(
    dados: schema_presenca.PresencaCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_presenca.registar_chamada(db, dados, current_user.escola_id)

@router.get("/presencas/{turma_id}/{data}")
def consultar_chamada(
    turma_id: int, 
    data: str, # Formato YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_presenca.ler_chamada_dia(db, turma_id, data)

@router.get("/presencas/turma/{turma_id}", response_model=List[schema_presenca.PresencaResponse])
def ler_chamada_lista(
    turma_id: int, 
    data: str, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    return crud_presenca.get_presencas_dia(db=db, turma_id=turma_id, data_busca=data_obj)

# --- Diário de Aula (Professor) ---

@router.post("/diarios/fechar")
def finalizar_aula(
    dados: schema_diario.DiarioCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    novo_diario = models_diario.Diario(
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
    current_user: models_user.Usuario = Depends(get_current_user)
):
    data_obj = datetime.strptime(data, "%Y-%m-%d").date()
    return crud_ponto.get_ponto_dia(db, current_user.escola_id, data_obj)

@router.post("/ponto-professores/")
def registrar_ponto_professores(
    payload: Dict[str, Any], 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    data_obj = datetime.strptime(payload['data'], "%Y-%m-%d").date()
    return crud_ponto.salvar_ponto(db, current_user.escola_id, payload['lista'], data_obj)

# @router.post("/presencas/", response_model=list[schema_presenca.PresencaResponse])
# def salvar_chamada(
#     dados: schema_presenca.ChamadaDiaria, 
#     db: Session = Depends(get_db),
#     current_user: models_user.Usuario = Depends(get_current_user)
# ):
#     return crud_presenca.registrar_chamada(db=db, chamada=dados)

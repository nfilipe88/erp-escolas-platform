from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas import schema_horario
from app.cruds import crud_horario
from app.cruds import crud_atribuicao
from app.models import horario as models_horario
from app.models import usuario as models_user
from app.security import get_current_user

router = APIRouter(prefix="/horarios", tags=["Horários"])

@router.put("/{id}")
def atualizar_slot(id: int, dados: schema_horario.HorarioCreate, db: Session = Depends(get_db)):
    slot = db.query(models_horario.Horario).filter(models_horario.Horario.id == id).first()
    if slot:
        slot.disciplina_id = dados.disciplina_id
        slot.professor_id = dados.professor_id
        db.commit()
    return slot

@router.get("/{id}/validar-tempo")
def validar_tempo_aula(id: int, db: Session = Depends(get_db)):
    slot = db.query(models_horario.Horario).filter(models_horario.Horario.id == id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Horário não encontrado")
    
    return crud_horario.verificar_acesso_chamada(slot)

    
# Rota para o PROFESSOR ver as suas turmas
@router.get("/minhas-aulas") # O schema de resposta pode ser genérico ou uma lista de dicionários
def ver_minhas_aulas(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Segurança: Apenas professores (ou admins curiosos)
    return crud_atribuicao.get_minhas_atribuicoes(db, professor_id=current_user.id) # type: ignore

# Rota para o PROFESSOR ver os seus horários do dia
@router.get("/meus-horarios-hoje")
def ver_meus_horarios_hoje(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Esta rota é "backend-side filtering" pura e rápida
    return crud_horario.get_horario_professor_hoje(db, professor_id=current_user.id)

# 1. Listar Horário da Turma (Para Secretária editar e Professor ver)
@router.get("/turmas/{turma_id}/horario")
def ver_horario(turma_id: int, db: Session = Depends(get_db)):
    return db.query(models_horario.Horario).filter(models_horario.Horario.turma_id == turma_id).order_by(models_horario.Horario.dia_semana, models_horario.Horario.hora_inicio).all()

# 2. Secretária: Gerar Grade Automática
@router.post("/turmas/{turma_id}/horario/gerar")
def gerar_horario_automatico(turma_id: int, db: Session = Depends(get_db), current_user: models_user.Usuario = Depends(get_current_user)):
    if current_user.perfil not in ['admin', 'secretaria', 'superadmin']:
        raise HTTPException(status_code=403, detail="Apenas secretaria pode gerar horários")
    return crud_horario.gerar_grade_horaria(db, turma_id, current_user.escola_id)
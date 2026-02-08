from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_turma as schemas_turma
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_disciplina as schemas_disciplina
from app.schemas import schema_horario
from app.cruds import crud_turma, crud_aluno, crud_disciplina, crud_horario
from app.models import usuario as models_user
from app.models import disciplina as models_disciplina
from app.models import horario as models_horario

router = APIRouter(prefix="/turmas", tags=["Turmas"])

@router.post("/", response_model=schemas_turma.TurmaCreate)
def criar_turma(
    turma: schemas_turma.TurmaCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    escola_destino_id = None
    if current_user.perfil == "superadmin":
        if not turma.escola_id:
            raise HTTPException(status_code=400, detail="Superadmin deve informar o ID da escola.")
        escola_destino_id = turma.escola_id
    else:
        escola_destino_id = current_user.escola_id
        if not escola_destino_id:
             raise HTTPException(status_code=400, detail="Utilizador não está associado a nenhuma escola.")

    return crud_turma.create_turma(db=db, turma=turma, escola_id=escola_destino_id)

@router.get("/", response_model=List[schemas_turma.TurmaResponse])
def ler_turmas(skip: int = 0, limit: int = 100, 
               db: Session = Depends(get_db),
               current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_turma.get_turmas_by_escola(db, escola_id=current_user.escola_id, skip=skip, limit=limit)

@router.get("/{turma_id}", response_model=schemas_turma.TurmaResponse)
def read_turma(turma_id: int, db: Session = Depends(get_db),
               current_user: models_user.Usuario = Depends(get_current_user)):
    db_turma = crud_turma.get_turma(db, turma_id=turma_id)
    if db_turma is None:
        raise HTTPException(status_code=404, detail="Turma não encontrada")
    return db_turma

@router.get("/{turma_id}/alunos", response_model=List[schemas_aluno.AlunoResponse])
def read_alunos_turma(turma_id: int, db: Session = Depends(get_db),
                      current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_aluno.get_alunos_por_turma(db=db, turma_id=turma_id)

# Gestão de Disciplinas da Turma
@router.get("/{turma_id}/disciplinas", response_model=List[schemas_disciplina.DisciplinaResponse])
def read_disciplinas_turma(turma_id: int, db: Session = Depends(get_db),
                           current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_disciplina.get_disciplinas_by_turma(db=db, turma_id=turma_id)

@router.post("/{turma_id}/associar-disciplina/{disciplina_id}")
def associar_disciplina_a_turma(turma_id: int, disciplina_id: int, 
                                db: Session = Depends(get_db),
                                current_user: models_user.Usuario = Depends(get_current_user)):
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")
    if disciplina in turma.disciplinas:
        return {"mensagem": "Disciplina já está associada a esta turma"}

    turma.disciplinas.append(disciplina)
    db.commit()
    return {"mensagem": f"Disciplina {disciplina.nome} adicionada à turma {turma.nome}"}

@router.delete("/{turma_id}/remover-disciplina/{disciplina_id}")
def remover_disciplina_de_turma(turma_id: int, disciplina_id: int, 
                                db: Session = Depends(get_db),
                                current_user: models_user.Usuario = Depends(get_current_user)):
    turma = crud_turma.get_turma(db, turma_id=turma_id)
    disciplina = db.query(models_disciplina.Disciplina).filter(models_disciplina.Disciplina.id == disciplina_id).first()

    if not turma or not disciplina:
        raise HTTPException(status_code=404, detail="Turma ou Disciplina não encontrada")
    
    if disciplina in turma.disciplinas:
        turma.disciplinas.remove(disciplina)
        db.commit()
        return {"mensagem": f"Disciplina {disciplina.nome} removida da turma."}
    return {"mensagem": "Esta disciplina já não pertence a esta turma."}

# Horários da Turma
@router.get("/{turma_id}/horario")
def ver_horario(turma_id: int, db: Session = Depends(get_db)):
    return db.query(models_horario.Horario).filter(models_horario.Horario.turma_id == turma_id)\
             .order_by(models_horario.Horario.dia_semana, models_horario.Horario.hora_inicio).all()

@router.post("/{turma_id}/horario/gerar")
def gerar_horario_automatico(turma_id: int, db: Session = Depends(get_db), 
                             current_user: models_user.Usuario = Depends(get_current_user)):
    if current_user.perfil not in ['admin', 'secretaria', 'superadmin']:
        raise HTTPException(status_code=403, detail="Apenas secretaria pode gerar horários")
    return crud_horario.gerar_grade_horaria(db, turma_id, current_user.escola_id)

@router.get("/escolas/{escola_id}/turmas", response_model=list[schemas_turma.TurmaResponse])
def read_turmas_escola(escola_id: int, db: Session = Depends(get_db),
                       current_user: models_user.Usuario = Depends(get_current_user)):
    return crud_turma.get_turmas_by_escola(db=db, escola_id=escola_id)
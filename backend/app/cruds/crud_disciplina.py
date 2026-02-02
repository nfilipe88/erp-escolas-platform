# app/cruds/crud_disciplina.py

from sqlalchemy.orm import Session
from app.models import disciplina as models
from app.schemas import schema_disciplina

def create_disciplina(db: Session, disciplina: schema_disciplina.DisciplinaCreate):
    # REMOVIDO o turma_id=disciplina.turma_id daqui
    db_disciplina = models.Disciplina(
        nome=disciplina.nome,
        codigo=disciplina.codigo,
        carga_horaria=disciplina.carga_horaria
    )
    db.add(db_disciplina)
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina

def get_disciplinas_by_turma(db: Session, turma_id: int):
    # Como agora é N:N, precisamos buscar a turma e retornar as suas disciplinas
    from app.models.turma import Turma
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if turma:
        return turma.disciplinas
    return []
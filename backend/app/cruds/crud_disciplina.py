# app/cruds/crud_disciplina.py
from sqlalchemy.orm import Session
from app.models import disciplina as models
from app.models.turma import Turma
from app.schemas import schema_disciplina
from typing import Optional

def create_disciplina(db: Session, disciplina: schema_disciplina.DisciplinaCreate, escola_id: int):
    db_obj = models.Disciplina(
        nome=disciplina.nome,
        codigo=disciplina.codigo,
        carga_horaria=disciplina.carga_horaria,
        escola_id=escola_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_disciplinas(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models.Disciplina)
    if escola_id:
        query = query.filter(models.Disciplina.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()

def get_disciplinas_by_turma(db: Session, turma_id: int, escola_id: Optional[int] = None):
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        return []
    # Filtra disciplinas que pertencem à escola especificada
    disciplinas = turma.disciplinas
    if escola_id:
        disciplinas = [d for d in disciplinas if d.escola_id == escola_id]
    return disciplinas
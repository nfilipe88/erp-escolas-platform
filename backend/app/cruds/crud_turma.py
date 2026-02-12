# app/cruds/crud_turma.py
from sqlalchemy.orm import Session
from app.models import turma as models
from app.schemas import schema_turma
from typing import Optional

def create_turma(db: Session, turma: schema_turma.TurmaCreate, escola_id: int):
    db_turma = models.Turma(
        nome=turma.nome,
        ano_letivo=turma.ano_letivo,
        escola_id=escola_id,
        turno=turma.turno,
    )
    db.add(db_turma)
    db.commit()
    db.refresh(db_turma)
    return db_turma

def get_turmas(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models.Turma)
    if escola_id:
        query = query.filter(models.Turma.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()

def get_turmas_by_escola(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Turma).filter(
        models.Turma.escola_id == escola_id
    ).offset(skip).limit(limit).all()

def get_turma(db: Session, turma_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Turma).filter(models.Turma.id == turma_id)
    if escola_id:
        query = query.filter(models.Turma.escola_id == escola_id)
    return query.first()
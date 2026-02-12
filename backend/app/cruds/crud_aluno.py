# app/cruds/crud_aluno.py
from sqlalchemy.orm import Session
from app.models import aluno as models
from app.schemas import schema_aluno
from typing import Optional

def get_aluno(db: Session, aluno_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.id == aluno_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.first()

def get_alunos(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models.Aluno)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()

def get_alunos_por_turma(db: Session, turma_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.turma_id == turma_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.all()

def create_aluno(db: Session, aluno: schema_aluno.AlunoCreate, escola_id: int):
    db_aluno = models.Aluno(
        nome=aluno.nome,
        bi=aluno.bi,
        data_nascimento=aluno.data_nascimento,
        escola_id=escola_id,
        turma_id=aluno.turma_id,
        ativo=aluno.ativo
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def update_aluno(db: Session, aluno_id: int, aluno_update: schema_aluno.AlunoUpdate,
                 escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.id == aluno_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    db_aluno = query.first()
    if not db_aluno:
        return None
    update_data = aluno_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_aluno, key, value)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def get_alunos_by_escola(db: Session, escola_id: int):
    return db.query(models.Aluno).filter(models.Aluno.escola_id == escola_id).all()

def get_aluno_by_bi(db: Session, bi: str, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.bi == bi)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.first()
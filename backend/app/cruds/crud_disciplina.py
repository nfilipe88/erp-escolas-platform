from sqlalchemy.orm import Session
from app.models import disciplina as models
from app.schemas import schema_disciplina
from app.models.turma import Turma

def create_disciplina(db: Session, disciplina: schema_disciplina.DisciplinaCreate, escola_id: int):
    db_obj = models.Disciplina(
        nome=disciplina.nome,
        codigo=disciplina.codigo,
        carga_horaria=disciplina.carga_horaria,
        escola_id=escola_id # <--- SEGURANÇA MÁXIMA
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_disciplinas(db: Session, skip: int, limit: int, escola_id: int = None):
    query = db.query(models.Disciplina)
    if escola_id:
        query = query.filter(models.Disciplina.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()

def get_disciplinas_by_turma(db: Session, turma_id: int):
    # Como agora é N:N, precisamos buscar a turma e retornar as suas disciplinas
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if turma:
        return turma.disciplinas
    return []
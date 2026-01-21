from sqlalchemy.orm import Session
from app.models import disciplina as models
from app.schemas import disciplina as schemas

def create_disciplina(db: Session, disciplina: schemas.DisciplinaCreate):
    db_disciplina = models.Disciplina(
        nome=disciplina.nome,
        turma_id=disciplina.turma_id
    )
    db.add(db_disciplina)
    db.commit()
    db.refresh(db_disciplina)
    return db_disciplina

def get_disciplinas_by_turma(db: Session, turma_id: int):
    return db.query(models.Disciplina).filter(models.Disciplina.turma_id == turma_id).all()
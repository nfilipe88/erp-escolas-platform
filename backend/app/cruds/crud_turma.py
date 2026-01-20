from sqlalchemy.orm import Session
from app.models import turma as models
from app.schemas import turma as schemas

def create_turma(db: Session, turma: schemas.TurmaCreate):
    db_turma = models.Turma(
        nome=turma.nome,
        ano_letivo=turma.ano_letivo,
        turno=turma.turno,
        escola_id=turma.escola_id
    )
    db.add(db_turma)
    db.commit()
    db.refresh(db_turma)
    return db_turma

def get_turmas_by_escola(db: Session, escola_id: int):
    return db.query(models.Turma).filter(models.Turma.escola_id == escola_id).all()
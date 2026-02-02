from sqlalchemy.orm import Session
from app.models import turma as models
from app.schemas import schema_turma

def create_turma(db: Session, turma: schema_turma.TurmaCreate, escola_id: int):
    db_turma = models.Turma(
        nome=turma.nome,
        ano_letivo=turma.ano_letivo,
        turno=turma.turno,
        escola_id=escola_id # <--- AQUI ESTÁ A SEGURANÇA!
    )
    db.add(db_turma)
    db.commit()
    db.refresh(db_turma)
    return db_turma

def get_turmas_by_escola(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Turma).filter(models.Turma.escola_id == escola_id).all()

def get_turma(db: Session, turma_id: int):
    return db.query(models.Turma).filter(models.Turma.id == turma_id).first()
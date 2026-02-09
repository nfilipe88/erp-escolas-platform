from sqlalchemy.orm import Session
from app.models import disciplina as models
from app.schemas import schema_disciplina
from app.models.turma import Turma

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
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if turma:
        return turma.disciplinas
    return []

def get_disciplinas(db: Session, skip: int = 0, limit: int = 100, escola_id: int = None):
    query = db.query(models.Disciplina)
    # SE o teu modelo Disciplina tiver o campo 'escola_id', descomenta as linhas abaixo:
    if escola_id:
        query = query.filter(models.Disciplina.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()
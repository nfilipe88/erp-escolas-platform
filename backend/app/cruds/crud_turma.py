# app/cruds/crud_turma.py
from sqlalchemy.orm import Session, selectinload 
from typing import Optional
from app.models.turma import Turma
from app.schemas import schema_turma

def create_turma(db: Session, turma: schema_turma.TurmaCreate, escola_id: int):
    db_turma = Turma(
        nome=turma.nome,
        ano_letivo=turma.ano_letivo,
        escola_id=escola_id,
        turno=turma.turno,
    )
    db.add(db_turma)
    db.commit()
    db.refresh(db_turma)
    return db_turma

def update_turma(db: Session, turma_id: int, turma: schema_turma.TurmaUpdate, escola_id: Optional[int] = None):
    db_turma = get_turma(db, turma_id, escola_id)
    if not db_turma:
        return None
    db_turma.nome = turma.nome
    if turma.ano_letivo is not None:
        db_turma.ano_letivo = turma.ano_letivo
    if turma.turno is not None:
        db_turma.turno = turma.turno
    db.commit()
    db.refresh(db_turma)
    return db_turma

# def get_turmas(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
#     query = db.query(Turma)
#     if escola_id:
#         query = query.filter(Turma.escola_id == escola_id)
#     return query.offset(skip).limit(limit).all()

def get_turmas_by_escola(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    return db.query(Turma).filter(
        Turma.escola_id == escola_id
    ).offset(skip).limit(limit).all()

# def get_turma(db: Session, turma_id: int, escola_id: Optional[int] = None):
#     query = db.query(Turma).filter(Turma.id == turma_id)
#     if escola_id:
#         query = query.filter(Turma.escola_id == escola_id)
#     return query.first()

def get_turmas(db: Session, escola_id: int, skip: int = 0, limit: int = 100):
    """
    Retorna a lista de turmas otimizada, carregando os alunos e atribuições antecipadamente.
    """
    return (
        db.query(Turma)
        .filter(Turma.escola_id == escola_id)
        # 2. Adicionar o options com selectinload
        # NOTA: Confirma se o nome do relacionamento no teu models/turma.py é "alunos". 
        # Se também quiseres carregar os professores/disciplinas, podes encadear mais.
        .options(
            selectinload(Turma.alunos),
            selectinload(Turma.atribuicoes), # Descomenta se quiseres carregar as atribuições também
            # selectinload(Turma.professores),
            selectinload(Turma.disciplinas)
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    
def get_turma(db: Session, turma_id: int, escola_id: int):
    """
    Retorna uma única turma, também otimizada.
    """
    return (
        db.query(Turma)
        .filter(Turma.id == turma_id, Turma.escola_id == escola_id)
        .options(
            selectinload(Turma.alunos)
        )
        .first()
    )
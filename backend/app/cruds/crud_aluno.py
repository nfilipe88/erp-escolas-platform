# app/cruds/crud_aluno.py
from sqlalchemy.orm import Session
from app.models import aluno as models
from app.schemas import aluno as schemas

def get_aluno(db: Session, aluno_id: int):
    return db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()

def get_alunos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Aluno).offset(skip).limit(limit).all()

# Esta função é usada pela Pauta Digital (nota-pauta)
def get_alunos_por_turma(db: Session, turma_id: int):
    return db.query(models.Aluno).filter(models.Aluno.turma_id == turma_id).all()

# Atualizamos a assinatura para aceitar 'escola_id' explicitamente
def create_aluno(db: Session, aluno: schemas.AlunoCreate, escola_id: int):
    db_aluno = models.Aluno(
        nome=aluno.nome,
        bi=aluno.bi,
        data_nascimento=aluno.data_nascimento,
        escola_id=escola_id, # <--- Usamos o ID seguro passado pelo main.py
        turma_id=aluno.turma_id
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

# def atualizar_aluno(db: Session, aluno_id: int, dados: schemas.AlunoUpdate):
#     # Nota: Usamos AlunoCreate aqui como genérico, idealmente seria AlunoUpdate
#     db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
#     if db_aluno:
#         # Atualiza campos dinamicamente
#         for key, value in dados.dict(exclude_unset=True).items():
#             # Proteção: não deixar mudar a escola_id num update simples se não quisermos
#             if key != 'escola_id': 
#                 setattr(db_aluno, key, value)
            
#         db.commit()
#         db.refresh(db_aluno)
#     return db_aluno
def update_aluno(db: Session, aluno_id: int, aluno_update: schemas.AlunoUpdate):
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    
    if not db_aluno:
        return None
    
    # Converter o Pydantic model para dict, excluindo campos não definidos
    update_data = aluno_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_aluno, key, value)
    
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def get_alunos_by_escola(db: Session, escola_id: int):
    return db.query(models.Aluno).filter(models.Aluno.escola_id == escola_id).all()

def get_aluno_by_bi(db: Session, bi: str):
    return db.query(models.Aluno).filter(models.Aluno.bi == bi).first()

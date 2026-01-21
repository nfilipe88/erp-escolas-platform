from sqlalchemy.orm import Session
from app.models import aluno as models
from app.schemas.aluno import AlunoCreate, AlunoUpdate

def create_aluno(db: Session, aluno: AlunoCreate):
    db_aluno = models.Aluno(
        nome=aluno.nome,
        bi=aluno.bi,
        data_nascimento=aluno.data_nascimento,
        escola_id=aluno.escola_id,
        turma_id=aluno.turma_id
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def get_alunos_by_escola(db: Session, escola_id: int):
    return db.query(models.Aluno).filter(models.Aluno.escola_id == escola_id).all()

def update_aluno(db: Session, aluno_id: int, aluno_update: AlunoUpdate):
    # Procura o aluno pelo ID
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    
    if not db_aluno:
        return None
    
    # Atualiza apenas os campos que foram enviados
    # (exclude_unset=True ignora o que não foi enviado)
    update_data = aluno_update.model_dump(exclude_unset=True) 
    
    for key, value in update_data.items():
        setattr(db_aluno, key, value)

    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def delete_aluno(db: Session, aluno_id: int):
    db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
    
    if db_aluno:
        db.delete(db_aluno)
        db.commit()
        return True
    return False

def get_alunos_by_turma(db: Session, turma_id: int):
    return db.query(models.Aluno).filter(models.Aluno.turma_id == turma_id).all()
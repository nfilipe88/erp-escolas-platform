# app/cruds/crud_atribuicao.py
from sqlalchemy.orm import Session
from app.models import atribuicao as models
from app.models import turma as models_turma
from app.schemas import schema_atribuicao
from typing import Optional

def create_atribuicao(db: Session, dados: schema_atribuicao.AtribuicaoCreate, escola_id: int):
    # Verifica se já existe atribuição para esta disciplina/turma (dentro da mesma escola)
    existente = db.query(models.Atribuicao).filter(
        models.Atribuicao.escola_id == escola_id,
        models.Atribuicao.turma_id == dados.turma_id,
        models.Atribuicao.disciplina_id == dados.disciplina_id
    ).first()

    if existente:
        existente.professor_id = dados.professor_id
        db.commit()
        db.refresh(existente)
        return existente

    db_atribuicao = models.Atribuicao(
        escola_id=escola_id,
        turma_id=dados.turma_id,
        disciplina_id=dados.disciplina_id,
        professor_id=dados.professor_id
    )
    db.add(db_atribuicao)
    db.commit()
    db.refresh(db_atribuicao)
    return db_atribuicao

def get_atribuicoes_escola(db: Session, escola_id: int):
    return db.query(models.Atribuicao).join(models_turma.Turma).filter(
        models_turma.Turma.escola_id == escola_id
    ).all()

def delete_atribuicao(db: Session, atribuicao_id: int, escola_id: int):
    item = db.query(models.Atribuicao).filter(
        models.Atribuicao.id == atribuicao_id,
        models.Atribuicao.escola_id == escola_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return item

def get_minhas_atribuicoes(db: Session, professor_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Atribuicao).filter(models.Atribuicao.professor_id == professor_id)
    if escola_id:
        query = query.filter(models.Atribuicao.escola_id == escola_id)
    return query.all()
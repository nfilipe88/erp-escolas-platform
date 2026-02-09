# app/cruds/crud_atribuicao.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import atribuicao as models
from app.models import turma as models_turma

from app.schemas import schema_atribuicao

# 1. CRIAR ATRIBUIÇÃO (Associar Professor)
def create_atribuicao(db: Session, dados: schema_atribuicao.AtribuicaoCreate, escola_id: int):
    # Verificar se já existe professor para esta disciplina nesta turma
    existente = db.query(models.Atribuicao).filter(
        models.Atribuicao.turma_id == dados.turma_id,
        models.Atribuicao.disciplina_id == dados.disciplina_id
    ).first()

    if existente:
        # Se já existe, atualizamos o professor (Troca de professor)
        existente.professor_id = dados.professor_id # type: ignore
        db.commit()
        db.refresh(existente)
        return existente
    
    # Se não existe, criamos novo
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

# 2. LISTAR POR ESCOLA (Com nomes bonitos)
def get_atribuicoes_escola(db: Session, escola_id: int= None):
    query = db.query(models.Atribuicao).join(models_turma.Turma)
    
    if escola_id:
        # Filtramos pela escola da TURMA associada à atribuição
        query = query.filter(models_turma.Turma.escola_id == escola_id)
        
    return query.all()

# 3. ELIMINAR (Remover professor da disciplina)
def delete_atribuicao(db: Session, atribuicao_id: int):
    item = db.query(models.Atribuicao).filter(models.Atribuicao.id == atribuicao_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

# 4. LISTAR TUDO O QUE EU (PROFESSOR) LECIONO
def get_minhas_atribuicoes(db: Session, professor_id: int):
    return db.query(models.Atribuicao).filter(models.Atribuicao.professor_id == professor_id).all()
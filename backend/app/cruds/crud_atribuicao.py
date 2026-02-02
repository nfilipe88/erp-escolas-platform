# app/cruds/crud_atribuicao.py
from sqlalchemy.orm import Session
from app.models import atribuicao as models
from app.schemas import schema_atribuicao
from fastapi import HTTPException

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
def get_atribuicoes_escola(db: Session, escola_id: int):
    resultados = db.query(models.Atribuicao).filter(models.Atribuicao.escola_id == escola_id).all()
    
    # Transformar objetos do banco em resposta bonita para o JSON
    lista_resposta = []
    for item in resultados:
        lista_resposta.append({
            "id": item.id,
            "turma_id": item.turma_id,
            "disciplina_id": item.disciplina_id,
            "professor_id": item.professor_id,
            # Extrair nomes das relações (Lazy Loading)
            "turma_nome": item.turma.nome if item.turma else "Turma Removida",
            "disciplina_nome": item.disciplina.nome if item.disciplina else "Disciplina Removida",
            "professor_nome": item.professor.nome if item.professor else "Professor Removido"
        })
    
    return lista_resposta

# 3. ELIMINAR (Remover professor da disciplina)
def delete_atribuicao(db: Session, atribuicao_id: int):
    item = db.query(models.Atribuicao).filter(models.Atribuicao.id == atribuicao_id).first()
    if item:
        db.delete(item)
        db.commit()
    return item

# 4. LISTAR TUDO O QUE EU (PROFESSOR) LECIONO
def get_minhas_atribuicoes(db: Session, professor_id: int):
    # Procura na tabela onde o ID do professor é o meu
    resultados = db.query(models.Atribuicao).filter(models.Atribuicao.professor_id == professor_id).all()
    
    lista_resposta = []
    for item in resultados:
        # Só adiciona se a turma e a disciplina ainda existirem (segurança)
        if item.turma and item.disciplina:
            lista_resposta.append({
                "id": item.id,
                "turma_id": item.turma_id,
                "turma_nome": f"{item.turma.nome} ({item.turma.turno})", # Ex: 7ª A (Manhã)
                "ano_letivo": item.turma.ano_letivo,
                "disciplina_id": item.disciplina_id,
                "disciplina_nome": item.disciplina.nome,
                "escola_id": item.escola_id
            })
            
    return lista_resposta
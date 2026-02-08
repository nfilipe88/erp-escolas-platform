from sqlalchemy.orm import Session
from datetime import date
from app.models import presenca as models_presenca
from app.schemas import schema_presenca

# 1. Registrar Chamada (Upsert: Cria ou Atualiza)
def registrar_chamada(db: Session, chamada: schema_presenca.ChamadaDiaria):
    registros_processados = []

    for item in chamada.lista_alunos:
        # Verifica se já existe registo para este aluno nesta data
        db_presenca = db.query(models_presenca.Presenca).filter(
            models_presenca.Presenca.aluno_id == item.aluno_id,
            models_presenca.Presenca.data == chamada.data
        ).first()

        if db_presenca:
            # ATUALIZA o existente
            db_presenca.presente = item.presente # type: ignore
            db_presenca.justificado = item.justificado # type: ignore
            db_presenca.observacao = item.observacao # type: ignore
        else:
            # CRIA um novo
            db_presenca = models_presenca.Presenca(
                turma_id=chamada.turma_id,
                data=chamada.data,
                aluno_id=item.aluno_id,
                presente=item.presente,
                justificado=item.justificado,
                observacao=item.observacao
            )
            db.add(db_presenca)
        
        registros_processados.append(db_presenca)
    
    db.commit()
    return registros_processados

# 2. Ler a chamada de um dia (para mostrar na tela se já foi feita)
def get_presencas_dia(db: Session, turma_id: int, data_busca: date):
    return db.query(models_presenca.Presenca).filter(
        models_presenca.Presenca.turma_id == turma_id,
        models_presenca.Presenca.data == data_busca
    ).all()

# 3. Contar faltas de um aluno (Para o Boletim)
def count_faltas_aluno(db: Session, aluno_id: int):
    return db.query(models_presenca.Presenca).filter(
        models_presenca.Presenca.aluno_id == aluno_id,
        models_presenca.Presenca.presente == False  # Só conta se faltou
    ).count()
    
def registar_chamada(db: Session, dados: schema_presenca.PresencaCreate, escola_id: int):
    # 1. Limpar registos anteriores dessa turma naquele dia (para evitar duplicados/conflitos)
    # Esta é a abordagem mais simples: apagar e reescrever o dia.
    db.query(models_presenca.Presenca).filter(
        models_presenca.Presenca.turma_id == dados.turma_id,
        models_presenca.Presenca.data == dados.data
    ).delete()
    
    # 2. Criar os novos registos
    novas_presencas = []
    for item in dados.lista:
        nova = models_presenca.Presenca(
            escola_id=escola_id,
            turma_id=dados.turma_id,
            aluno_id=item.aluno_id,
            data=dados.data,
            status=item.status
        )
        novas_presencas.append(nova)
    
    db.add_all(novas_presencas)
    db.commit()
    return {"msg": "Chamada registada com sucesso", "total": len(novas_presencas)}

def ler_chamada_dia(db: Session, turma_id: int, data: str):
    return db.query(models_presenca.Presenca).filter(
        models_presenca.Presenca.turma_id == turma_id,
        models_presenca.Presenca.data == data
    ).all()
from sqlalchemy.orm import Session
from app.models import presenca as models
from app.schemas import presenca as schemas
from datetime import date

# 1. Registrar Chamada (Upsert: Cria ou Atualiza)
def registrar_chamada(db: Session, chamada: schemas.ChamadaDiaria):
    registros_processados = []

    for item in chamada.lista_alunos:
        # Verifica se já existe registo para este aluno nesta data
        db_presenca = db.query(models.Presenca).filter(
            models.Presenca.aluno_id == item.aluno_id,
            models.Presenca.data == chamada.data
        ).first()

        if db_presenca:
            # ATUALIZA o existente
            db_presenca.presente = item.presente # type: ignore
            db_presenca.justificado = item.justificado # type: ignore
            db_presenca.observacao = item.observacao # type: ignore
        else:
            # CRIA um novo
            db_presenca = models.Presenca(
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
    return db.query(models.Presenca).filter(
        models.Presenca.turma_id == turma_id,
        models.Presenca.data == data_busca
    ).all()

# 3. Contar faltas de um aluno (Para o Boletim)
def count_faltas_aluno(db: Session, aluno_id: int):
    return db.query(models.Presenca).filter(
        models.Presenca.aluno_id == aluno_id,
        models.Presenca.presente == False  # Só conta se faltou
    ).count()
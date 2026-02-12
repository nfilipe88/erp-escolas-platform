# app/cruds/crud_presenca.py
from sqlalchemy.orm import Session
from datetime import date
from app.models import presenca, aluno, turma
from app.schemas import schema_presenca
from typing import Optional

def registrar_chamada(db: Session, chamada: schema_presenca.ChamadaDiaria, escola_id: int):
    # Apagar registos anteriores do dia para esta turma
    db.query(presenca.Presenca).filter(
        presenca.Presenca.turma_id == chamada.turma_id,
        presenca.Presenca.data == chamada.data
    ).delete()

    novas_presencas = []
    for item in chamada.lista:
        nova = presenca.Presenca(
            escola_id=escola_id,
            turma_id=chamada.turma_id,
            aluno_id=item.aluno_id,
            data=chamada.data,
            presente=(item.status == 'P'),
            justificado=(item.status == 'FJ'),
            status=item.status,
            observacao=item.observacao
        )
        novas_presencas.append(nova)

    db.add_all(novas_presencas)
    db.commit()
    return novas_presencas

def get_presencas_dia(db: Session, turma_id: int, data_busca: date, escola_id: Optional[int] = None):
    query = db.query(presenca.Presenca).filter(
        presenca.Presenca.turma_id == turma_id,
        presenca.Presenca.data == data_busca
    )
    if escola_id:
        query = query.filter(presenca.Presenca.escola_id == escola_id)
    return query.all()

def count_faltas_aluno(db: Session, aluno_id: int, escola_id: Optional[int] = None):
    query = db.query(presenca.Presenca).filter(
        presenca.Presenca.aluno_id == aluno_id,
        presenca.Presenca.presente == False
    )
    if escola_id:
        query = query.filter(presenca.Presenca.escola_id == escola_id)
    return query.count()

# Removida função duplicada 'registar_chamada' (versão antiga)
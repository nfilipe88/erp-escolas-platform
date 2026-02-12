# app/cruds/crud_horario.py
from sqlalchemy.orm import Session
from app.schemas import schema_horario
from datetime import datetime, timedelta, time
from typing import Optional

from app.models import horario as models_horario
from app.models import diario as models_diario
from app.models import turma as models_turma
from app.models import disciplina as models_disciplina

def get_horario_professor_hoje(db: Session, professor_id: int, escola_id: Optional[int] = None):
    dia_hoje = datetime.now().weekday()
    query = db.query(models_horario.Horario)\
        .join(models_turma.Turma)\
        .filter(
            models_horario.Horario.professor_id == professor_id,
            models_horario.Horario.dia_semana == dia_hoje
        )
    if escola_id:
        query = query.filter(models_turma.Turma.escola_id == escola_id)
    return query.order_by(models_horario.Horario.hora_inicio).all()

def get_todos_horarios(db: Session, escola_id: Optional[int] = None):
    query = db.query(models_horario.Horario).join(models_turma.Turma)
    if escola_id:
        query = query.filter(models_turma.Turma.escola_id == escola_id)
    return query.all()

def gerar_grade_horaria(db: Session, turma_id: int, escola_id: int):
    # Verificar se a turma pertence à escola
    turma = db.query(models_turma.Turma).filter(
        models_turma.Turma.id == turma_id,
        models_turma.Turma.escola_id == escola_id
    ).first()
    if not turma:
        return {"error": "Turma não encontrada ou não pertence a esta escola"}

    tempos_manha = [
        (time(7, 30), time(8, 15)),
        (time(8, 20), time(9, 5)),
        (time(9, 10), time(9, 55)),
        (time(10, 15), time(11, 0)),
        (time(11, 5), time(11, 50))
    ]

    db.query(models_horario.Horario).filter(models_horario.Horario.turma_id == turma_id).delete()

    novos = []
    for dia in range(0, 5):
        for inicio, fim in tempos_manha:
            item = models_horario.Horario(
                escola_id=escola_id,
                turma_id=turma_id,
                dia_semana=dia,
                hora_inicio=inicio,
                hora_fim=fim,
                disciplina_id=None,
                professor_id=None
            )
            novos.append(item)

    db.add_all(novos)
    db.commit()
    return {"msg": "Grade gerada com sucesso"}

def verificar_acesso_chamada(horario: models_horario.Horario):
    agora = datetime.now()
    dia_atual = agora.weekday()
    if horario.dia_semana != dia_atual:
        return {"pode": False, "msg": "Hoje não é dia desta aula."}

    margem = 10
    hoje_data = agora.date()
    dt_inicio = datetime.combine(hoje_data, horario.hora_inicio) - timedelta(minutes=margem)
    dt_fim = datetime.combine(hoje_data, horario.hora_fim) + timedelta(minutes=margem)

    if dt_inicio <= agora <= dt_fim:
        return {"pode": True, "msg": "Autorizado"}
    if agora < dt_inicio:
        return {"pode": False, "msg": f"Ainda é cedo. Aguarde {horario.hora_inicio}"}
    return {"pode": False, "msg": "Tempo de chamada expirou."}

def fechar_diario(db: Session, diario_id: int, escola_id: int):
    diario = db.query(models_diario.Diario).filter(
        models_diario.Diario.id == diario_id,
        models_diario.Diario.escola_id == escola_id
    ).first()
    if diario:
        diario.fechado = True
        db.commit()
        db.refresh(diario)
    return diario
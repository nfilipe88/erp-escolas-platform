# app/cruds/crud_horario.py
from sqlalchemy.orm import Session
from app.schemas import schema_horario
from datetime import datetime, timedelta, time, date

from app.models import horario as models_horario
from app.models import diario as models_diario
from app.models import turma as models_turma
from app.models import disciplina as models_disciplina
from app.models import usuario as models_usuario

def get_horario_professor_hoje(db: Session, professor_id: int):
    # 0=Segunda, 1=Terça ... 4=Sexta, 5=Sábado, 6=Domingo
    dia_hoje = datetime.now().weekday()
    
    # Busca apenas as aulas DESTE professor para HOJE, ordenadas por hora
    aulas = db.query(models_horario.Horario)\
              .join(models_turma.Turma)\
              .join(models_disciplina.Disciplina)\
              .filter(models_horario.Horario.professor_id == professor_id)\
              .filter(models_horario.Horario.dia_semana == dia_hoje)\
              .order_by(models_horario.Horario.hora_inicio)\
              .all()
              
    # Nota: Como temos relacionamentos (lazy='joined' ou padrão), 
    # o Pydantic vai conseguir ler 'turma.nome' e 'disciplina.nome' na resposta.
    return aulas

# 1. GERAÇÃO AUTOMÁTICA DE SLOTS (Para facilitar a vida da secretária)
def gerar_grade_horaria(db: Session, turma_id: int, escola_id: int):
    # Cria uma estrutura padrão: 2ª a 6ª, 5 tempos por dia
    # Exemplo: Manhã (07:30 - 12:30)
    tempos_manha = [
        (time(7, 30), time(8, 15)),
        (time(8, 20), time(9, 0o5)),
        (time(9, 10), time(9, 55)), # Intervalo antes
        (time(10, 15), time(11, 00)),
        (time(11, 0o5), time(11, 50))
    ]
    
    # Apaga horários antigos desta turma (Limpeza)
    db.query(models_horario.Horario).filter(models_horario.Horario.turma_id == turma_id).delete()
    
    novos = []
    # 0=Segunda ... 4=Sexta
    for dia in range(0, 5): 
        for inicio, fim in tempos_manha:
            # Cria slot vazio (sem disciplina/professor ainda)
            # A secretária depois vai editar e atribuir
            item = models_horario.Horario(
                escola_id=escola_id,
                turma_id=turma_id,
                dia_semana=dia,
                hora_inicio=inicio,
                hora_fim=fim,
                disciplina_id=None, # Vazio
                professor_id=None   # Vazio
            )
            novos.append(item)
    
    db.add_all(novos)
    db.commit()
    return {"msg": "Grade gerada com sucesso"}

# 2. VALIDAR SE PROFESSOR PODE FAZER CHAMADA AGORA ⏰
def verificar_acesso_chamada(horario: models_horario.Horario):
    agora = datetime.now()
    hora_atual = agora.time()
    # dia_semana do python: 0=Segunda ... 6=Domingo
    dia_atual = agora.weekday() 

    # Regra 1: Dia Errado
    if horario.dia_semana != dia_atual:
        return {"pode": False, "msg": "Hoje não é dia desta aula."}

    # Regra 2: Tolerância (Ex: Pode entrar 10min antes e sair 10min depois)
    margem = 10 # minutos
    
    # Converter para datetime completo para fazer contas matemáticas
    hoje_data = agora.date()
    dt_inicio = datetime.combine(hoje_data, horario.hora_inicio) - timedelta(minutes=margem)
    dt_fim = datetime.combine(hoje_data, horario.hora_fim) + timedelta(minutes=margem)

    if dt_inicio <= agora <= dt_fim:
        return {"pode": True, "msg": "Autorizado"}
    
    if agora < dt_inicio:
        return {"pode": False, "msg": f"Ainda é cedo. Aguarde {horario.hora_inicio}"}
    
    return {"pode": False, "msg": "Tempo de chamada expirou."}

# 3. FINALIZAR AULA (Enviar para Secretária)
def fechar_diario(db: Session, diario_id: int):
    diario = db.query(models_diario.Diario).filter(models_diario.Diario.id == diario_id).first()
    if diario:
        diario.fechado = True # Bloqueia edição do professor
        db.commit()
    return diario
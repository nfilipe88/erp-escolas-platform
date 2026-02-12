# app/cruds/crud_dashboard.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import aluno, usuario, turma, escola, disciplina, mensalidade
from typing import Optional

def get_stats(db: Session, escola_id: Optional[int] = None):
    q_alunos = db.query(aluno.Aluno)
    q_professores = db.query(usuario.Usuario).filter(usuario.Usuario.perfil == 'professor')
    q_turmas = db.query(turma.Turma)
    q_escolas = db.query(escola.Escola)
    q_disciplinas = db.query(disciplina.Disciplina)
    q_receita = db.query(func.sum(mensalidade.Mensalidade.valor_base)).filter(
        mensalidade.Mensalidade.estado == "PAGO"
    )

    if escola_id:
        q_alunos = q_alunos.filter(aluno.Aluno.escola_id == escola_id)
        q_professores = q_professores.filter(usuario.Usuario.escola_id == escola_id)
        q_turmas = q_turmas.filter(turma.Turma.escola_id == escola_id)
        q_disciplinas = q_disciplinas.filter(disciplina.Disciplina.escola_id == escola_id)
        q_receita = q_receita.join(aluno.Aluno).filter(aluno.Aluno.escola_id == escola_id)
        total_escolas = 1
    else:
        total_escolas = q_escolas.count()

    return {
        "total_alunos": q_alunos.count(),
        "total_professores": q_professores.count(),
        "total_turmas": q_turmas.count(),
        "total_escolas": total_escolas,
        "alunos_ativos": q_alunos.filter(aluno.Aluno.ativo == True).count(),
        "total_disciplinas": q_disciplinas.count(),
        "receita_estimada": q_receita.scalar() or 0.0
    }
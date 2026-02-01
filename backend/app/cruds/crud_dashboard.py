from sqlalchemy.orm import Session
from app.models import escola as models_escola
from app.models import turma as models_turma
from app.models import aluno as models_aluno
from app.models import disciplina as models_disciplina

def get_stats(db: Session):
    total_alunos = db.query(models_aluno.Aluno).count()
    
    # Cálculo Simples da Receita: Alunos * 35.000 (Valor médio)
    # Num futuro upgrade, podemos somar o valor exato configurado de cada escola.
    receita = total_alunos * 5000.0
    return {
        "total_escolas": db.query(models_escola.Escola).count(),
        "total_turmas": db.query(models_turma.Turma).count(),
        # "total_alunos": db.query(models_aluno.Aluno).count(),
        "total_alunos": total_alunos,
        # Conta apenas alunos onde ativo é Verdadeiro
        "alunos_ativos": db.query(models_aluno.Aluno).filter(models_aluno.Aluno.ativo == True).count(),
        "total_disciplinas": db.query(models_disciplina.Disciplina).count(),
        "receita_estimada": receita  # Placeholder para receita estimada
    }
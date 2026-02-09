from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import aluno, usuario, turma, escola, disciplina, mensalidade

def get_stats(db: Session, escola_id: int = None):
    # Queries base
    q_alunos = db.query(aluno.Aluno)
    q_professores = db.query(usuario.Usuario).filter(usuario.Usuario.perfil == 'professor')
    q_turmas = db.query(turma.Turma)
    q_escolas = db.query(escola.Escola)
    q_disciplinas = db.query(disciplina.Disciplina)
    
    # Cálculo de receita: soma de 'valor_pago' onde status é 'PAGO'
    q_receita = db.query(func.sum(mensalidade.Mensalidade.valor_base)).filter(mensalidade.Mensalidade.estado == "PAGO")

    # Aplicar filtro de segurança (Multi-Tenant)
    if escola_id:
        q_alunos = q_alunos.filter(aluno.Aluno.escola_id == escola_id)
        q_professores = q_professores.filter(usuario.Usuario.escola_id == escola_id)
        q_turmas = q_turmas.filter(turma.Turma.escola_id == escola_id)
        
        # Para a receita, precisamos de garantir que a mensalidade é de um aluno desta escola
        q_receita = q_receita.join(aluno.Aluno).filter(aluno.Aluno.escola_id == escola_id)
        
        # Quem não é superadmin vê apenas 1 escola (a sua)
        total_escolas_count = 1
    else:
        total_escolas_count = q_escolas.count()

    # Executa a query de receita. Se for None, devolve 0.0
    val_receita = q_receita.scalar() or 0.0

    return {
        "total_alunos": q_alunos.count(),
        "total_professores": q_professores.count(),
        "total_turmas": q_turmas.count(),
        "total_escolas": total_escolas_count,
        "alunos_ativos": q_alunos.filter(aluno.Aluno.ativo == True).count(), # Certifica-te que o modelo Aluno tem 'ativo'
        "total_disciplinas": q_disciplinas.count(),
        "receita_estimada": val_receita
    }
# app/routers/dashboard.py
# app/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.db.database import get_db
from app.models import aluno as models_aluno
from app.models import turma as models_turma
from app.models import usuario as models_user
from app.models import atribuicao as models_atribuicao
from app.models import disciplina as models_disciplina
from app.security import get_current_user

router = APIRouter() 

@router.get("/resumo")
def get_dashboard_resumo(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # 1. Identificar o Perfil Principal
    roles = [getattr(r, 'name', getattr(r, 'nome', 'user')).lower() for r in current_user.roles]
    perfil = "user"
    if "superadmin" in roles or "admin" in roles:
        perfil = "admin"
    elif "professor" in roles:
        perfil = "professor"
    elif "aluno" in roles:
        perfil = "aluno"
    elif "secretaria" in roles:
        perfil = "secretaria"

    response_data = {
        "perfil": perfil,
        "cards": [],
        "graficos": []
    }

    # 2. Lógica Específica por Perfil
    
    # --- ADMIN / SECRETARIA ---
    if perfil in ["admin", "secretaria", "superadmin"]:
        
        # Escudo para 'ativo' no Aluno
        if hasattr(models_aluno.Aluno, 'ativo'):
            total_alunos = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.ativo == True).count()
        else:
            total_alunos = db.query(models_aluno.Aluno).count()
            
        # Escudo para 'ativo' na Turma (Isto resolve o teu erro!)
        if hasattr(models_turma.Turma, 'ativo'):
            total_turmas = db.query(models_turma.Turma).filter(models_turma.Turma.ativo == True).count()
        else:
            total_turmas = db.query(models_turma.Turma).count()
            
        total_users = db.query(models_user.Usuario).count()
        
        # Escudo para a coluna 'descricao' ou 'nome' no Gráfico
        grafico_turmas = []
        if hasattr(models_turma.Turma, 'descricao'):
            turmas_por_grau = db.query(models_turma.Turma.descricao, func.count(models_turma.Turma.id))\
                .group_by(models_turma.Turma.descricao).all()
            grafico_turmas = [{"name": t[0] or "Geral", "value": t[1]} for t in turmas_por_grau]
        else:
            # Fallback se não existir coluna 'descricao'
            grafico_turmas = [{"name": "Total de Turmas", "value": total_turmas}]

        response_data["cards"] = [
            {"titulo": "Total Alunos", "valor": total_alunos, "cor": "blue", "icon": "people"},
            {"titulo": "Total de Turmas", "valor": total_turmas, "cor": "green", "icon": "class"},
            {"titulo": "Utilizadores", "valor": total_users, "cor": "purple", "icon": "settings"},
        ]
        response_data["graficos"] = {
            "principal": grafico_turmas,
            "tipo": "pie"
        }

    # --- PROFESSOR ---
    elif perfil == "professor":
        minhas_turmas = db.query(models_atribuicao.Atribuicao.turma_id)\
            .filter(models_atribuicao.Atribuicao.professor_id == current_user.id)\
            .distinct().count()
            
        minhas_disciplinas = db.query(models_atribuicao.Atribuicao.disciplina_id)\
            .filter(models_atribuicao.Atribuicao.professor_id == current_user.id)\
            .distinct().count()
            
        q_alunos = db.query(models_aluno.Aluno)\
            .join(models_turma.Turma)\
            .join(models_atribuicao.Atribuicao, models_atribuicao.Atribuicao.turma_id == models_turma.Turma.id)\
            .filter(models_atribuicao.Atribuicao.professor_id == current_user.id)\
            .count()

        response_data["cards"] = [
            {"titulo": "Minhas Turmas", "valor": minhas_turmas, "cor": "indigo", "icon": "school"},
            {"titulo": "Meus Alunos", "valor": q_alunos, "cor": "teal", "icon": "groups"},
            {"titulo": "Disciplinas", "valor": minhas_disciplinas, "cor": "orange", "icon": "book"},
        ]
        response_data["graficos"] = {
            "principal": [{"name": "Turmas", "value": minhas_turmas}, {"name": "Disciplinas", "value": minhas_disciplinas}],
            "tipo": "bar"
        }

    # --- ALUNO ---
    elif perfil == "aluno":
        aluno = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.email == current_user.email).first()
        
        turma_nome = "Sem Turma"
        if aluno and aluno.turma:
            turma_nome = aluno.turma.nome

        response_data["cards"] = [
            {"titulo": "Minha Turma", "valor": turma_nome, "cor": "blue", "icon": "class"},
            {"titulo": "Média Global", "valor": "14.5", "cor": "green", "icon": "grade"},
            {"titulo": "Faltas", "valor": 2, "cor": "red", "icon": "warning"},
        ]

    return response_data

print("🟢 FIM - dashboard.py carregado. Rotas finais:", [route.path for route in router.routes])
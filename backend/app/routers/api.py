# app/routers/api.py
from fastapi import APIRouter
from app.routers import (
    auth, alunos, usuarios, escolas, turmas, disciplinas, notas, 
    dashboard, horarios, presenca, financeiro, atribuicoes, mensalidade, configuracoes, roles
)

api_router = APIRouter()

# Agrupando todas as rotas
api_router.include_router(auth.router, tags=["Autenticação"])

# CORREÇÃO CRÍTICA: O prefixo fica APENAS aqui. 
# Isto garante que a rota final será /dashboard/resumo
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

api_router.include_router(alunos.router, prefix="/alunos", tags=["Alunos"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["Usuários"])
api_router.include_router(escolas.router, prefix="/escolas", tags=["Escolas"])
api_router.include_router(turmas.router, prefix="/turmas", tags=["Turmas"])
api_router.include_router(disciplinas.router, prefix="/disciplinas", tags=["Disciplinas"])
api_router.include_router(notas.router, prefix="/notas", tags=["Notas"])
api_router.include_router(horarios.router, prefix="/horarios", tags=["Horários"])
api_router.include_router(presenca.router, prefix="/presenca", tags=["Presença"])
api_router.include_router(financeiro.router, prefix="/financeiro", tags=["Financeiro"])
api_router.include_router(atribuicoes.router, prefix="/atribuicoes", tags=["Atribuições"])
api_router.include_router(mensalidade.router, prefix="/mensalidades", tags=["Mensalidades"])
api_router.include_router(configuracoes.router, prefix="/minha-escola", tags=["Configurações"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
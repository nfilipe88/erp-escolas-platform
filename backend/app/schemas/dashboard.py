from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_escolas: int
    total_turmas: int
    total_alunos: int
    alunos_ativos: int
    total_disciplinas: int
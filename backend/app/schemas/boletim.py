from pydantic import BaseModel
from typing import List, Optional

# Representa uma nota individual no boletim
class NotaBoletim(BaseModel):
    trimestre: str
    valor: float
    descricao: str

# Representa uma linha do boletim (Uma disciplina com várias notas)
class LinhaBoletim(BaseModel):
    disciplina: str
    notas: List[NotaBoletim]
    media_provisoria: float # Calculamos isto no backend

# O Boletim completo
class BoletimResponse(BaseModel):
    aluno_nome: str
    aluno_bi: Optional[str]
    turma: str
    linhas: List[LinhaBoletim]
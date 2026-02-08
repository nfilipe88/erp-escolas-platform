from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# Modelo base de um registo
class PresencaBase(BaseModel):
    aluno_id: int
    presente: bool
    justificado: bool = False
    observacao: Optional[str] = None
    status: Optional[str] = None  # 'P', 'F', 'FJ'

# O que vem do Frontend quando clicamos "Salvar Chamada"
class ChamadaDiaria(BaseModel):
    turma_id: int
    data: date
    lista_alunos: List[PresencaBase] # Uma lista com o estado de cada aluno
    
# Validação individual de cada aluno na lista
class PresencaItem(BaseModel):
    aluno_id: int
    status: str  # Ex: 'P', 'F', 'FJ'

# O que devolvemos ao Frontend para ler
# class PresencaResponse(PresencaBase):
#     id: int
#     data: date
#     turma_id: int
    
class PresencaResponse(BaseModel):
    msg: str
    total: int
    
class PresencaCreate(BaseModel):
    turma_id: int
    data: date
    lista: List[PresencaBase] # Recebe a lista completa da turma
    
    class Config:
        from_attributes = True
# app/schemas/atribuicao.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Para mostrar dados bonitos (com nomes em vez de IDs)
class AtribuicaoResponse(BaseModel):
    id: int
    turma_id: int
    disciplina_id: int
    professor_id: int
    
    turma_nome: str      # Vamos extrair o nome da relação
    disciplina_nome: str # Vamos extrair o nome da relação
    professor_nome: str  # Vamos extrair o nome da relação    

# Para receber dados do Frontend
class AtribuicaoCreate(BaseModel):
    turma_id: int
    disciplina_id: int
    professor_id: int    
    
    model_config = ConfigDict(from_attributes=True)
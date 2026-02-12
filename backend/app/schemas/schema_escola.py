from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Optional

class EscolaBase(BaseModel):
    nome: str
    slug: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

class EscolaCreate(EscolaBase):
    pass

class EscolaResponse(EscolaBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UsuarioResumo(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

class EscolaDetalhes(EscolaResponse):
    total_alunos: int
    alunos_ativos: int
    alunos_inativos: int
    total_turmas: int
    total_usuarios: int
    contagem_por_perfil: Dict[str, int]
    lista_diretores: List[UsuarioResumo]
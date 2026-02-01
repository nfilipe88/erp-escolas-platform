# backend/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

# 1. Base: Campos comuns que usamos tanto para criar como para ler
class EscolaBase(BaseModel):
    nome: str
    slug: str
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None

# 2. Create: O que precisamos para criar (validar input)
class EscolaCreate(EscolaBase):
    pass # Herda tudo de cima (nome, slug, endereco)

# 3. Response: O que devolvemos ao utilizador (inclui ID e datas)
class EscolaResponse(EscolaBase):
    id: int
    is_active: bool
    created_at: datetime

# Objeto para listar os Diretores/Admins na tela de detalhes
class UsuarioResumo(BaseModel):
    id: int
    nome: str
    email: str
    perfil: str

# O RELATÓRIO COMPLETO (O Raio-X da Escola)
class EscolaDetalhes(EscolaResponse):
    # Métricas de Alunos
    total_alunos: int
    alunos_ativos: int
    alunos_inativos: int
    
    # Métricas de Estrutura
    total_turmas: int
    
    # Métricas de Pessoal
    total_usuarios: int
    contagem_por_perfil: Dict[str, int] # Ex: {"professor": 10, "secretaria": 2}
    lista_diretores: List[UsuarioResumo] # Quem manda na escola

    class Config:
        from_attributes = True
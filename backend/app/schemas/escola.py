# backend/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 1. Base: Campos comuns que usamos tanto para criar como para ler
class EscolaBase(BaseModel):
    nome: str
    slug: str
    endereco: Optional[str] = None

# 2. Create: O que precisamos para criar (validar input)
class EscolaCreate(EscolaBase):
    pass # Herda tudo de cima (nome, slug, endereco)

# 3. Response: O que devolvemos ao utilizador (inclui ID e datas)
class EscolaResponse(EscolaBase):
    id: int
    ativo: bool
    created_at: datetime

    # Configuração necessária para o Pydantic ler dados do SQLAlchemy
    class Config:
        from_attributes = True
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional

# Schema básico de Role para exibição
class RoleBase(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    nome: str
    email: EmailStr
    senha: str
    roles: List[int] = []
    escola_id: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    id: int
    nome: str
    email: EmailStr
    ativo: bool=True
    escola_id: Optional[int] = None
    roles: List[RoleBase] = [] # Retorna a lista completa de roles
    permissoes: List[str] = [] # Opcional: enviar permissões calculadas para o front saber o que mostrar

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    roles: List[RoleBase] = []         # ← aqui sim, pois Token não herda de UsuarioBase
    nome: str
    escola_id: Optional[int] = None

class SenhaUpdate(BaseModel):
    senha_atual: str
    nova_senha: str

    model_config = ConfigDict(from_attributes=True)
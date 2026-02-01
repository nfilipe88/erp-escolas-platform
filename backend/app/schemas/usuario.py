from typing import Optional
from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    perfil: str # 'admin', 'professor', 'secretaria', 'superadmin'
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str
    escola_id: Optional[int] = None # Opcional na entrada

class UsuarioResponse(UsuarioBase):
    id: int
    escola_id: Optional[int]

# Schema para o Token (Login realizado com sucesso)
class Token(BaseModel):
    access_token: str
    token_type: str
    perfil: str
    nome: str
    
class SenhaUpdate(BaseModel):
    senha_atual: str
    nova_senha: str    
    
    class Config:
        from_attributes = True
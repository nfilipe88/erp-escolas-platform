from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from app.models.usuario import PerfilUsuario

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    perfil: PerfilUsuario
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str
    escola_id: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    id: int
    escola_id: Optional[int]
    # NÃO redefinir 'perfil' aqui – herdado de UsuarioBase

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    perfil: str          # ← aqui sim, pois Token não herda de UsuarioBase
    nome: str

class SenhaUpdate(BaseModel):
    senha_atual: str
    nova_senha: str

    model_config = ConfigDict(from_attributes=True)
from pydantic import BaseModel, EmailStr

class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str
    perfil: str = "professor"

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioResponse(UsuarioBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True

# Schema para o Token (Login realizado com sucesso)
class Token(BaseModel):
    access_token: str
    token_type: str
    perfil: str
    nome: str
    
class SenhaUpdate(BaseModel):
    senha_atual: str
    nova_senha: str
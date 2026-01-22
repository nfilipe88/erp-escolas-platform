from pydantic import BaseModel

class EmailRequest(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    nova_senha: str
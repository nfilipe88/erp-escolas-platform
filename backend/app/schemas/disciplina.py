from pydantic import BaseModel

class DisciplinaBase(BaseModel):
    nome: str
    turma_id: int

class DisciplinaCreate(DisciplinaBase):
    pass

class DisciplinaResponse(DisciplinaBase):
    id: int

    class Config:
        from_attributes = True
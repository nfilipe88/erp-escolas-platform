# app/schemas/schema_horario.py
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import time
from enum import Enum

class DiaSemana(str, Enum):
    SEGUNDA = "Segunda-feira"
    TERCA = "Terça-feira"
    QUARTA = "Quarta-feira"
    QUINTA = "Quinta-feira"
    SEXTA = "Sexta-feira"
    SABADO = "Sábado"
    DOMINGO = "Domingo"

class HorarioBase(BaseModel):
    dia_semana: DiaSemana
    hora_inicio: time
    hora_fim: time
    sala: Optional[str] = None

    @field_validator('hora_fim')
    def validar_horario(cls, v, values):
        if 'hora_inicio' in values.data and v <= values.data['hora_inicio']:
            raise ValueError('A hora de fim deve ser posterior à hora de início')
        return v

class HorarioCreate(HorarioBase):
    turma_id: int
    disciplina_id: int
    professor_id: Optional[int] = None # Opcional, pois pode ser atribuído depois

class HorarioUpdate(BaseModel):
    dia_semana: Optional[DiaSemana] = None
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None
    sala: Optional[str] = None
    professor_id: Optional[int] = None

class HorarioResponse(HorarioBase):
    id: int
    escola_id: int
    turma_id: int
    disciplina_id: int
    professor_id: Optional[int] = None
    
    # Nomes para facilitar o frontend
    disciplina_nome: Optional[str] = None
    professor_nome: Optional[str] = None
    turma_nome: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
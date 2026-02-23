# app/services/horario_service.py
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import time

from app.models.horario import Horario
from app.models.turma import Turma
from app.models.disciplina import Disciplina
from app.models.usuario import Usuario
from app.schemas import schema_horario

class HorarioService:
    def __init__(self, db: Session):
        self.db = db

    def _verificar_conflito(self, dia: str, inicio: time, fim: time, turma_id: int = None, professor_id: int = None, ignorar_id: int = None):
        """
        Verifica se existe choque de horário para a turma ou para o professor.
        """
        query = self.db.query(Horario).filter(
            Horario.dia_semana == dia,
            Horario.hora_inicio < fim,
            Horario.hora_fim > inicio
        )

        if ignorar_id:
            query = query.filter(Horario.id != ignorar_id)

        # 1. Conflito de Turma (A turma não pode ter duas aulas ao mesmo tempo)
        if turma_id:
            conflito_turma = query.filter(Horario.turma_id == turma_id).first()
            if conflito_turma:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Choque de horário! A turma já tem aula de '{conflito_turma.disciplina.nome}' neste período."
                )

        # 2. Conflito de Professor (O professor não pode estar em dois lugares)
        if professor_id:
            conflito_prof = query.filter(Horario.professor_id == professor_id).first()
            if conflito_prof:
                raise HTTPException(
                    status_code=400, 
                    detail=f"O professor já está a dar aula na turma '{conflito_prof.turma.nome}' neste horário."
                )

    def criar_horario(self, dados: schema_horario.HorarioCreate, usuario_logado: Usuario) -> Horario:
        # 1. Validar Escola/Permissões
        turma = self.db.query(Turma).filter(Turma.id == dados.turma_id).first()
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada.")
        
        if usuario_logado.perfil != "superadmin" and usuario_logado.escola_id != turma.escola_id:
            raise HTTPException(status_code=403, detail="Sem permissão nesta escola.")

        # 2. Verificar se Disciplina pertence à turma/escola
        disciplina = self.db.query(Disciplina).filter(Disciplina.id == dados.disciplina_id).first()
        if not disciplina or disciplina.escola_id != turma.escola_id:
            raise HTTPException(status_code=400, detail="Disciplina inválida.")

        # 3. Validar Conflitos
        self._verificar_conflito(
            dia=dados.dia_semana, 
            inicio=dados.hora_inicio, 
            fim=dados.hora_fim, 
            turma_id=dados.turma_id, 
            professor_id=dados.professor_id
        )

        # 4. Criar
        novo_horario = Horario(
            turma_id=dados.turma_id,
            disciplina_id=dados.disciplina_id,
            professor_id=dados.professor_id,
            escola_id=turma.escola_id,
            dia_semana=dados.dia_semana,
            hora_inicio=dados.hora_inicio,
            hora_fim=dados.hora_fim,
            sala=dados.sala
        )
        self.db.add(novo_horario)
        self.db.commit()
        self.db.refresh(novo_horario)
        return novo_horario

    def listar_por_turma(self, turma_id: int, usuario_logado: Usuario) -> List[Horario]:
        """Retorna a grade horária da turma ordenada"""
        turma = self.db.query(Turma).filter(Turma.id == turma_id).first()
        if not turma:
             raise HTTPException(status_code=404, detail="Turma não encontrada.")
        
        if usuario_logado.perfil != "superadmin" and usuario_logado.escola_id != turma.escola_id:
             raise HTTPException(status_code=403, detail="Acesso negado.")

        # Ordenar por Dia (custom logic needed for days) e Hora
        # Aqui simplificamos ordenando por hora, o frontend agrupa por dia
        return self.db.query(Horario).filter(Horario.turma_id == turma_id).order_by(Horario.hora_inicio).all()

    def listar_por_professor(self, professor_id: int, usuario_logado: Usuario) -> List[Horario]:
        """Para o professor ver a sua própria agenda"""
        if usuario_logado.perfil != "superadmin" and usuario_logado.id != professor_id:
             # Se for coordenador, pode ver. Se for outro professor, não (regra opcional)
             if usuario_logado.perfil != "admin":
                raise HTTPException(status_code=403, detail="Acesso negado.")

        return self.db.query(Horario).filter(Horario.professor_id == professor_id).all()

    def deletar_horario(self, horario_id: int, usuario_logado: Usuario):
        horario = self.db.query(Horario).filter(Horario.id == horario_id).first()
        if not horario:
            raise HTTPException(status_code=404, detail="Horário não encontrado.")
            
        if usuario_logado.perfil not in ["admin", "superadmin"]:
             raise HTTPException(status_code=403, detail="Apenas admin pode remover horários.")

        self.db.delete(horario)
        self.db.commit()
# app/services/presenca_service.py
from typing import List
from datetime import date
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.presenca import Presenca
from app.models.turma import Turma
from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.schemas import schema_presenca

class PresencaService:
    def __init__(self, db: Session):
        self.db = db

    def _validar_acesso_turma(self, usuario: Usuario, turma_id: int):
        """Verifica se usuario tem acesso à turma (mesma escola)"""
        turma = self.db.query(Turma).filter(Turma.id == turma_id).first()
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada.")
            
        if usuario.perfil != "superadmin":
            if usuario.escola_id != turma.escola_id:
                raise HTTPException(status_code=403, detail="Acesso negado a esta turma.")
        return turma

    def realizar_chamada(self, dados: schema_presenca.RealizarChamadaRequest, usuario_logado: Usuario):
        """
        Processa uma lista de presenças para uma turma/dia.
        Se já existir registo para o aluno naquele dia/disciplina, ATUALIZA.
        Se não, CRIA.
        """
        turma = self._validar_acesso_turma(usuario_logado, dados.turma_id)

        registros_processados = []

        for item in dados.alunos:
            # 1. Validar se aluno é da turma (segurança extra)
            # Otimização: Poderíamos carregar IDs dos alunos da turma em memória antes do loop
            
            # 2. Verificar existência
            presenca_existente = self.db.query(Presenca).filter(
                Presenca.aluno_id == item.aluno_id,
                Presenca.turma_id == dados.turma_id,
                Presenca.disciplina_id == dados.disciplina_id,
                Presenca.data == dados.data
            ).first()

            if presenca_existente:
                # Atualizar
                presenca_existente.status = item.status
                presenca_existente.observacao = item.observacao
                registros_processados.append(presenca_existente)
            else:
                # Criar
                nova_presenca = Presenca(
                    aluno_id=item.aluno_id,
                    turma_id=dados.turma_id,
                    disciplina_id=dados.disciplina_id,
                    escola_id=turma.escola_id,
                    data=dados.data,
                    status=item.status,
                    observacao=item.observacao
                )
                self.db.add(nova_presenca)
                registros_processados.append(nova_presenca)
        
        self.db.commit()
        return {"mensagem": f"{len(registros_processados)} registos de presença processados com sucesso."}

    def listar_por_turma_data(self, turma_id: int, disciplina_id: int, data: date, usuario_logado: Usuario) -> List[Presenca]:
        """Retorna a folha de chamada de um dia específico"""
        self._validar_acesso_turma(usuario_logado, turma_id)
        
        presencas = self.db.query(Presenca).filter(
            Presenca.turma_id == turma_id,
            Presenca.disciplina_id == disciplina_id,
            Presenca.data == data
        ).all()
        
        return presencas

    def atualizar_presenca(self, presenca_id: int, dados: schema_presenca.PresencaUpdate, usuario_logado: Usuario):
        """Corrige um registro individual"""
        presenca = self.db.query(Presenca).filter(Presenca.id == presenca_id).first()
        if not presenca:
            raise HTTPException(status_code=404, detail="Registo não encontrado.")
            
        if usuario_logado.perfil != "superadmin" and usuario_logado.escola_id != presenca.escola_id:
             raise HTTPException(status_code=403, detail="Acesso negado.")

        if dados.status:
            presenca.status = dados.status
        if dados.observacao is not None:
            presenca.observacao = dados.observacao
            
        self.db.commit()
        self.db.refresh(presenca)
        return presenca

    def calcular_frequencia_aluno(self, aluno_id: int, disciplina_id: int, usuario_logado: Usuario):
        """Estatísticas para o Boletim/Dashboard"""
        aluno = self.db.query(Aluno).filter(Aluno.id == aluno_id).first()
        if not aluno:
             raise HTTPException(status_code=404, detail="Aluno não encontrado.")
             
        if usuario_logado.perfil != "superadmin" and usuario_logado.escola_id != aluno.escola_id:
             raise HTTPException(status_code=403, detail="Acesso negado.")

        # Query total
        presencas = self.db.query(Presenca).filter(
            Presenca.aluno_id == aluno_id,
            Presenca.disciplina_id == disciplina_id
        ).all()
        
        total = len(presencas)
        if total == 0:
            return {"total_aulas": 0, "frequencia": 100}
            
        faltas = len([p for p in presencas if p.status == "Ausente"])
        presencas_reais = total - faltas
        
        percentual = (presencas_reais / total) * 100
        
        return {
            "total_aulas": total,
            "total_faltas": faltas,
            "percentual_frequencia": round(percentual, 1)
        }
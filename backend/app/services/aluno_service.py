# backend/app/services/aluno_service.py - NOVO ARQUIVO
from datetime import date
from sqlalchemy.orm import Session
from typing import Optional, List
from app.cruds import crud_aluno
from app.schemas import schema_aluno
from app.models import aluno as models
from app.core.exceptions import BusinessLogicError
from app.services.email_service import EmailService
from app.services.audit_service import AuditService
from app.cruds import crud_mensalidade, crud_turma

class AlunoService:
    """Serviço para lógica de negócio de alunos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        self.audit_service = AuditService(db)
    
    def matricular_aluno(
        self,
        dados: schema_aluno.AlunoCreate,
        escola_id: int,
        usuario_id: int
    ) -> models.Aluno:
        """Matricular novo aluno com validações de negócio"""
        
        # 1. Validar se turma existe e pertence à escola
        if dados.turma_id:
            turma = crud_turma.get_turma(self.db, dados.turma_id, escola_id)
            if not turma:
                raise BusinessLogicError("Turma não encontrada ou não pertence a esta escola")
            
            # Verificar capacidade da turma
            alunos_turma = crud_aluno.get_alunos_por_turma(self.db, dados.turma_id)
            if len(alunos_turma) >= 40:  # Limite configurável
                raise BusinessLogicError("Turma lotada (máximo 40 alunos)")
        
        # 2. Verificar duplicação de BI
        if dados.bi:
            aluno_existente = crud_aluno.get_aluno_by_bi(self.db, dados.bi, escola_id)
            if aluno_existente:
                raise BusinessLogicError(f"Já existe aluno com BI {dados.bi}")
        
        # 3. Validar idade mínima
        if dados.data_nascimento:
            idade = (date.today() - dados.data_nascimento).days // 365
            if idade < 3:
                raise BusinessLogicError("Aluno deve ter no mínimo 3 anos")
        
        # 4. Criar aluno
        aluno = crud_aluno.create_aluno(self.db, dados, escola_id)
        
        # 5. Registrar auditoria
        self.audit_service.log_action(
            usuario_id=usuario_id,
            action="MATRICULA_ALUNO",
            entity_type="Aluno",
            entity_id=aluno.id,
            details={"nome": aluno.nome, "escola_id": escola_id}
        )
        
        # 6. Enviar email de boas-vindas (assíncrono)
        if dados.email:
            self.email_service.enviar_boas_vindas(aluno.email, aluno.nome)
        
        return aluno
    
    def transferir_turma(
        self,
        aluno_id: int,
        nova_turma_id: int,
        escola_id: int,
        usuario_id: int,
        motivo: str
    ) -> models.Aluno:
        """Transferir aluno de turma com validações"""
        
        # 1. Buscar aluno
        aluno = crud_aluno.get_aluno(self.db, aluno_id, escola_id)
        if not aluno:
            raise BusinessLogicError("Aluno não encontrado")
        
        # 2. Verificar se nova turma existe e tem capacidade
        nova_turma = crud_turma.get_turma(self.db, nova_turma_id, escola_id)
        if not nova_turma:
            raise BusinessLogicError("Turma destino não encontrada")
        
        alunos_nova_turma = crud_aluno.get_alunos_por_turma(self.db, nova_turma_id)
        if len(alunos_nova_turma) >= 40:
            raise BusinessLogicError("Turma destino está lotada")
        
        # 3. Guardar turma antiga para histórico
        turma_antiga_id = aluno.turma_id
        
        # 4. Atualizar aluno
        aluno.turma_id = nova_turma_id
        self.db.commit()
        self.db.refresh(aluno)
        
        # 5. Registrar na auditoria
        self.audit_service.log_action(
            usuario_id=usuario_id,
            action="TRANSFERENCIA_TURMA",
            entity_type="Aluno",
            entity_id=aluno.id,
            details={
                "turma_antiga": turma_antiga_id,
                "turma_nova": nova_turma_id,
                "motivo": motivo
            }
        )
        
        return aluno
    
    def desativar_aluno(
        self,
        aluno_id: int,
        escola_id: int,
        usuario_id: int,
        motivo: str
    ) -> models.Aluno:
        """Desativar aluno (não deleta, preserva histórico)"""
        
        aluno = crud_aluno.get_aluno(self.db, aluno_id, escola_id)
        if not aluno:
            raise BusinessLogicError("Aluno não encontrado")
        
        if not aluno.ativo:
            raise BusinessLogicError("Aluno já está inativo")
        
        # Verificar se tem mensalidades pendentes
        mensalidades_pendentes = crud_mensalidade.get_mensalidades_aluno(
            self.db, aluno_id, escola_id
        )
        pendentes = [m for m in mensalidades_pendentes if m.estado == "Pendente"]
        
        if pendentes:
            raise BusinessLogicError(
                f"Aluno possui {len(pendentes)} mensalidades pendentes. "
                "Regularize antes de desativar."
            )
        
        # Desativar
        aluno.ativo = False
        self.db.commit()
        
        # Auditoria
        self.audit_service.log_action(
            usuario_id=usuario_id,
            action="DESATIVACAO_ALUNO",
            entity_type="Aluno",
            entity_id=aluno.id,
            details={"motivo": motivo}
        )
        
        return aluno
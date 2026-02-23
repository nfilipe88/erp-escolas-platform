from typing import List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.turma import Turma
from app.models.usuario import Usuario
from app.models.disciplina import Disciplina
from app.schemas import schema_turma
from app.cruds import crud_turma, crud_aluno, crud_disciplina, crud_horario
from app.core.exceptions import BusinessLogicError
from app.security_decorators import has_role, has_any_role

class TurmaService:
    def __init__(self, db: Session):
        self.db = db

    # --- Métodos Básicos (CRUD) ---
    
    def get_by_id(self, turma_id: int, usuario_logado: Usuario) -> Turma:
        escola_id = usuario_logado.escola_id if not has_role(usuario_logado, "superadmin") else None
        turma = crud_turma.get_turma(self.db, turma_id, escola_id)
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada ou acesso negado.")
        return turma

    def listar(self, usuario_logado: Usuario, skip: int = 0, limit: int = 100) -> List[Turma]:
        escola_id = usuario_logado.escola_id if not has_role(usuario_logado, "superadmin") else None
        return crud_turma.get_turmas(self.db, skip=skip, limit=limit, escola_id=escola_id)

    def criar(self, dados: schema_turma.TurmaCreate, usuario_logado: Usuario) -> Turma:
        escola_target_id = dados.escola_id
        if not has_role(usuario_logado, "superadmin"):
            if not usuario_logado.escola_id:
                raise HTTPException(status_code=400, detail="Usuário sem escola associada.")
            escola_target_id = usuario_logado.escola_id
        elif not escola_target_id:
            raise HTTPException(status_code=400, detail="Superadmin deve informar escola_id.")

        return crud_turma.create_turma(self.db, dados, escola_id=escola_target_id)

    def atualizar(self, turma_id: int, dados: schema_turma.TurmaUpdate, usuario_logado: Usuario) -> Turma:
        self.get_by_id(turma_id, usuario_logado) # Garante permissão
        escola_id = usuario_logado.escola_id if usuario_logado.roles != "superadmin" else None
        return crud_turma.update_turma(self.db, turma_id, dados, escola_id)

    def deletar(self, turma_id: int, usuario_logado: Usuario) -> None:
        if not has_any_role(usuario_logado, ["admin", "superadmin"]):
            raise HTTPException(status_code=403, detail="Apenas Admin pode remover turmas.")
        
        turma = self.get_by_id(turma_id, usuario_logado)
        
        # Validação Crítica: Não apagar turma com alunos
        alunos = crud_aluno.get_alunos_por_turma(self.db, turma_id, escola_id=turma.escola_id)
        if alunos:
            raise HTTPException(status_code=400, detail=f"Turma possui {len(alunos)} alunos. Impossível remover.")
        
        self.db.delete(turma)
        self.db.commit()

    # --- Métodos de Relacionamento (NOVOS) ---

    def listar_alunos(self, turma_id: int, usuario_logado: Usuario):
        """Lista alunos da turma validando acesso"""
        turma = self.get_by_id(turma_id, usuario_logado)
        return crud_aluno.get_alunos_por_turma(self.db, turma_id, escola_id=turma.escola_id)

    def listar_disciplinas(self, turma_id: int, usuario_logado: Usuario):
        """Lista disciplinas associadas à turma"""
        turma = self.get_by_id(turma_id, usuario_logado)
        # Assume que crud_disciplina tem este método, ou usamos a relação do ORM
        return turma.disciplinas 

    def associar_disciplina(self, turma_id: int, disciplina_id: int, usuario_logado: Usuario):
        """Associa uma disciplina a uma turma (Matriz Curricular)"""
        # 1. Validar Turma
        turma = self.get_by_id(turma_id, usuario_logado)
        
        # 2. Validar Disciplina
        disciplina = self.db.query(Disciplina).filter(
            Disciplina.id == disciplina_id,
            Disciplina.escola_id == turma.escola_id # Tem que ser da mesma escola!
        ).first()
        
        if not disciplina:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada nesta escola.")

        # 3. Associar
        if disciplina not in turma.disciplinas:
            turma.disciplinas.append(disciplina)
            self.db.commit()
            return {"mensagem": f"Disciplina '{disciplina.nome}' adicionada à turma '{turma.nome}'"}
        
        return {"mensagem": "Disciplina já estava associada."}

    def remover_disciplina(self, turma_id: int, disciplina_id: int, usuario_logado: Usuario):
        """Remove disciplina da grade da turma"""
        turma = self.get_by_id(turma_id, usuario_logado)
        
        disciplina = next((d for d in turma.disciplinas if d.id == disciplina_id), None)
        if not disciplina:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada nesta turma.")
            
        turma.disciplinas.remove(disciplina)
        self.db.commit()
        return {"mensagem": "Disciplina removida da turma."}

    # --- Métodos de Horário ---

    def ver_horario(self, turma_id: int, usuario_logado: Usuario):
        """Retorna o horário da turma"""
        turma = self.get_by_id(turma_id, usuario_logado)
        # Usando crud_horario se existir, ou query direta
        return crud_horario.get_horario_turma(self.db, turma_id)

    def gerar_horario_automatico(self, turma_id: int, usuario_logado: Usuario):
        """Gera horário automático (Lógica complexa delegada ao CRUD/Algoritmo)"""
        if not has_any_role(usuario_logado, ["admin", "superadmin"]):
             raise HTTPException(status_code=403, detail="Apenas admins podem gerar horários.")
             
        turma = self.get_by_id(turma_id, usuario_logado)
        return crud_horario.gerar_grade_horaria(self.db, turma_id, turma.escola_id)
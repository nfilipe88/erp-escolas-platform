from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Any, Dict, List, Optional

from app.models.aluno import Aluno
from app.models.usuario import Usuario
from app.schemas import schema_aluno
from app.cruds import crud_aluno, crud_turma
from app.core.config import settings
from app.cruds import crud_nota

class AlunoService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, aluno_id: int, escola_id: Optional[int]) -> Aluno:
        """Busca um aluno garantindo que pertence à escola do utilizador"""
        aluno = crud_aluno.get_aluno(self.db, aluno_id, escola_id)
        if not aluno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Aluno não encontrado ou não pertence a esta escola"
            )
        return aluno

    def matricular(self, dados: schema_aluno.AlunoCreate, usuario_logado: Usuario) -> Aluno:
        """
        Cria um novo aluno aplicando regras de negócio:
        1. Valida permissão de escola (Superadmin vs Admin de Escola)
        2. Verifica capacidade da turma
        3. Verifica duplicidade de BI
        """
        
        # 1. Definição do ID da Escola
        escola_target_id = dados.escola_id
        
        if usuario_logado.perfil != "superadmin":
            # Se não é superadmin, forçamos o ID da escola do utilizador logado
            if not usuario_logado.escola_id:
                raise HTTPException(status_code=400, detail="Utilizador sem escola associada.")
            escola_target_id = usuario_logado.escola_id
        else:
            # Se é superadmin, ele DEVE informar para qual escola está criando
            if not escola_target_id:
                raise HTTPException(status_code=400, detail="Superadmin deve informar o ID da escola.")

        # 2. Validação de Turma (Capacidade)
        if dados.turma_id:
            turma = crud_turma.get_turma(self.db, dados.turma_id, escola_target_id)
            if not turma:
                raise HTTPException(status_code=404, detail="Turma não encontrada nesta escola.")
            
            # Contar alunos na turma (Regra de Negócio)
            qtd_alunos = len(crud_aluno.get_alunos_por_turma(self.db, dados.turma_id))
            # O limite poderia vir do settings ou da tabela turma
            limite = getattr(settings, 'MAX_ALUNOS_TURMA', 40) 
            
            if qtd_alunos >= limite:
                raise HTTPException(
                    status_code=400, 
                    detail=f"A turma está cheia. Limite atual: {limite} alunos."
                )

        # 3. Validação de BI Duplicado
        if dados.bi:
            aluno_existente = crud_aluno.get_aluno_by_bi(self.db, dados.bi, escola_target_id)
            if aluno_existente:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Já existe um aluno com o BI '{dados.bi}' nesta escola."
                )

        # 4. Criação
        novo_aluno = crud_aluno.create_aluno(self.db, dados, escola_target_id)
        return novo_aluno

    def atualizar(self, aluno_id: int, dados: schema_aluno.AlunoUpdate, usuario_logado: Usuario) -> Aluno:
        """Atualiza aluno verificando permissões"""
        escola_id = usuario_logado.escola_id if usuario_logado.perfil != "superadmin" else None
        
        # Verifica existência
        aluno = self.get_by_id(aluno_id, escola_id)
        
        # Se tentar mudar de turma, devíamos validar capacidade novamente (Fica para melhoria futura)
        
        return crud_aluno.update_aluno(self.db, aluno_id, dados, escola_id)

    def listar(self, usuario_logado: Usuario, skip: int = 0, limit: int = 100) -> List[Aluno]:
        """Lista alunos da escola do utilizador"""
        escola_id = usuario_logado.escola_id if usuario_logado.perfil != "superadmin" else None
        return crud_aluno.get_alunos(self.db, skip, limit, escola_id)
    
    def deletar(self, aluno_id: int, usuario_logado: Usuario) -> None:
        """Remove um aluno. Apenas Admin ou Superadmin podem fazer isso."""
        
        # 1. Verificar permissões de perfil
        if usuario_logado.perfil not in ["admin", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem remover alunos."
            )

        # 2. Definir contexto da escola
        escola_id = usuario_logado.escola_id if usuario_logado.perfil != "superadmin" else None

        # 3. Buscar e validar existência/pertença
        aluno = self.get_by_id(aluno_id, escola_id) # Já lança 404 se não achar

        # 4. (Opcional) Verificar regras de negócio impeditivas
        # Ex: Não deletar se tiver notas ou financeiro pendente.
        # Por enquanto, seguimos o delete simples.
        
        crud_aluno.delete_aluno(self.db, aluno.id) # Precisará criar este método no CRUD se não existir, ou usar db.delete direto
        # Caso o CRUD não tenha delete_aluno, use:
        # self.db.delete(aluno)
        # self.db.commit()

    def obter_boletim(self, aluno_id: int, usuario_logado: Usuario) -> Dict[str, Any]:
        """Busca o boletim garantindo a segurança dos dados"""
        escola_id = usuario_logado.escola_id if usuario_logado.perfil != "superadmin" else None
        
        # Valida se aluno existe e pertence à escola
        self.get_by_id(aluno_id, escola_id)

        # Busca o boletim
        boletim = crud_nota.get_boletim_aluno(self.db, aluno_id, escola_id=escola_id)
        
        if not boletim:
            raise HTTPException(status_code=404, detail="Boletim não disponível ou aluno sem notas.")
            
        return boletim

    def listar_por_turma(self, turma_id: int, usuario_logado: Usuario) -> List[Aluno]:
        """Lista alunos de uma turma específica"""
        escola_id = usuario_logado.escola_id if usuario_logado.perfil != "superadmin" else None

        # 1. Validar a Turma
        turma = crud_turma.get_turma(self.db, turma_id, escola_id=escola_id)
        if not turma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Turma não encontrada ou não pertence a esta escola."
            )

        # 2. Buscar Alunos
        return crud_aluno.get_alunos_por_turma(self.db, turma_id, escola_id)
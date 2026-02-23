# app/services/disciplina_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.disciplina import Disciplina
from app.models.usuario import Usuario
from app.schemas import schema_disciplina
from app.cruds import crud_disciplina
from app.security_decorators import has_role, has_any_role

class DisciplinaService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, disciplina_id: int, usuario_logado: Usuario) -> Disciplina:
        """Busca disciplina garantindo acesso à escola correta"""
        escola_id = usuario_logado.escola_id if not has_role(usuario_logado, "superadmin") else None
        
        disciplina = crud_disciplina.get_disciplina(self.db, disciplina_id)
        
        # Validações
        if not disciplina:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada.")
        
        if escola_id and disciplina.escola_id != escola_id:
            raise HTTPException(status_code=403, detail="Acesso negado a esta disciplina.")
            
        return disciplina

    def listar(self, usuario_logado: Usuario, skip: int = 0, limit: int = 100) -> List[Disciplina]:
        """Lista disciplinas da escola do utilizador"""
        escola_id = usuario_logado.escola_id if not has_role(usuario_logado, "superadmin") else None
        return crud_disciplina.get_disciplinas(self.db, skip, limit, escola_id)

    def listar_por_escola(self, escola_id: int, usuario_logado: Usuario) -> List[Disciplina]:
        """
        Lista disciplinas de uma escola específica.
        Útil para Superadmins ou para validações internas.
        """
        # Se não for superadmin, só pode ver a sua própria escola
        if not has_role(usuario_logado, "superadmin") and usuario_logado.escola_id != escola_id:
            raise HTTPException(status_code=403, detail="Não tem permissão para visualizar disciplinas desta escola.")
            
        return crud_disciplina.get_disciplinas(self.db, skip=0, limit=1000, escola_id=escola_id)

    def criar(self, dados: schema_disciplina.DisciplinaCreate, usuario_logado: Usuario) -> Disciplina:
        """Cria disciplina com validação de duplicidade"""
        
        # 1. Definir Escola Alvo
        escola_target_id = dados.escola_id
        if not has_role(usuario_logado, "superadmin"):
            if not usuario_logado.escola_id:
                raise HTTPException(status_code=400, detail="Usuário sem escola associada.")
            escola_target_id = usuario_logado.escola_id
        elif not escola_target_id:
            raise HTTPException(status_code=400, detail="Superadmin deve informar escola_id.")

        # 2. Verificar Duplicidade (Nome exato na mesma escola)
        # Idealmente o CRUD teria get_by_name, mas podemos fazer verificação simples aqui se o CRUD não tiver
        existente = self.db.query(Disciplina).filter(
            Disciplina.nome == dados.nome,
            Disciplina.escola_id == escola_target_id
        ).first()
        
        if existente:
            raise HTTPException(status_code=400, detail=f"A disciplina '{dados.nome}' já existe nesta escola.")

        return crud_disciplina.create_disciplina(self.db, dados, escola_id=escola_target_id)

    def atualizar(self, disciplina_id: int, dados: schema_disciplina.DisciplinaUpdate, usuario_logado: Usuario) -> Disciplina:
        self.get_by_id(disciplina_id, usuario_logado) # Garante permissão
        
        escola_id = usuario_logado.escola_id if not has_role(usuario_logado, "superadmin") else None
        return crud_disciplina.update_disciplina(self.db, disciplina_id, dados, escola_id)

    def deletar(self, disciplina_id: int, usuario_logado: Usuario) -> None:
        """
        Remove disciplina com verificação de INTEGRIDADE.
        Não pode apagar se estiver em uso (Turmas ou Notas).
        """
        if not has_any_role(usuario_logado, ["admin", "superadmin"]):
             raise HTTPException(status_code=403, detail="Apenas admins podem remover disciplinas.")

        disciplina = self.get_by_id(disciplina_id, usuario_logado)

        # 1. Verificar se está associada a alguma turma
        if disciplina.turmas and len(disciplina.turmas) > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Não é possível apagar. Disciplina associada a {len(disciplina.turmas)} turmas."
            )

        # 2. Verificar se tem notas lançadas
        if disciplina.notas and len(disciplina.notas) > 0:
            raise HTTPException(
                status_code=400, 
                detail="Não é possível apagar. Existem notas lançadas para esta disciplina."
            )

        self.db.delete(disciplina)
        self.db.commit()
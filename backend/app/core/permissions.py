# backend/app/core/permissions.py - NOVO ARQUIVO
import asyncio
from enum import Enum
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.permission import Permission, 
from app.models import Roles
from app.db.database import get_db
from app.core.auth import get_current_user

class ResourceEnum(str, Enum):
    """Recursos do sistema"""
    ALUNOS = "alunos"
    TURMAS = "turmas"
    PROFESSORES = "professores"
    NOTAS = "notas"
    MENSALIDADES = "mensalidades"
    PRESENCAS = "presencas"
    USUARIOS = "usuarios"
    DISCIPLINAS = "disciplinas"
    HORARIOS = "horarios"
    RELATORIOS = "relatorios"
    CONFIGURACOES = "configuracoes"

class ActionEnum(str, Enum):
    """Ações possíveis"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    APPROVE = "approve"

class PermissionService:
    """Serviço para gerenciar permissões"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_default_permissions(self):
        """Criar permissões padrão do sistema"""
        
        permissions_data = []
        
        # Gerar permissões para cada recurso
        for resource in ResourceEnum:
            for action in [ActionEnum.CREATE, ActionEnum.READ, ActionEnum.UPDATE, ActionEnum.DELETE]:
                permissions_data.append({
                    "name": f"{resource.value}:{action.value}",
                    "resource": resource.value,
                    "action": action.value,
                    "description": f"{action.value.title()} {resource.value}"
                })
        
        # Adicionar permissões especiais
        special_permissions = [
            {"name": "relatorios:export", "resource": "relatorios", "action": "export", 
             "description": "Exportar relatórios"},
            {"name": "mensalidades:approve", "resource": "mensalidades", "action": "approve",
             "description": "Aprovar pagamentos"},
            {"name": "configuracoes:manage", "resource": "configuracoes", "action": "update",
             "description": "Gerenciar configurações da escola"},
        ]
        
        permissions_data.extend(special_permissions)
        
        # Criar no banco
        for perm_data in permissions_data:
            existing = self.db.query(Permission).filter(
                Permission.name == perm_data["name"]
            ).first()
            
            if not existing:
                permission = Permission(**perm_data)
                self.db.add(permission)
        
        self.db.commit()
    
    def create_default_roles(self):
        """Criar roles padrão do sistema"""
        
        # 1. Superadmin - todas as permissões
        superadmin = self.db.query(Role).filter(Role.name == "superadmin").first()
        if not superadmin:
            superadmin = Role(
                name="superadmin",
                description="Administrador do sistema",
                is_system_role=True
            )
            self.db.add(superadmin)
            self.db.flush()
            
            # Adicionar todas as permissões
            all_permissions = self.db.query(Permission).all()
            superadmin.permissions.extend(all_permissions)
        
        # 2. Admin Escola - gerenciar sua escola
        admin_escola = self.db.query(Role).filter(Role.name == "admin_escola").first()
        if not admin_escola:
            admin_escola = Role(
                name="admin_escola",
                description="Administrador da escola",
                is_system_role=True
            )
            self.db.add(admin_escola)
            self.db.flush()
            
            # Permissões do admin escola
            escola_permissions = self.db.query(Permission).filter(
                Permission.name.in_([
                    "alunos:create", "alunos:read", "alunos:update", "alunos:delete",
                    "turmas:create", "turmas:read", "turmas:update", "turmas:delete",
                    "professores:create", "professores:read", "professores:update", "professores:delete",
                    "notas:read", "notas:update",
                    "mensalidades:create", "mensalidades:read", "mensalidades:update",
                    "mensalidades:approve",
                    "presencas:read",
                    "usuarios:create", "usuarios:read", "usuarios:update",
                    "relatorios:read", "relatorios:export",
                    "configuracoes:manage"
                ])
            ).all()
            admin_escola.permissions.extend(escola_permissions)
        
        # 3. Professor - gerenciar turmas e notas
        professor = self.db.query(Role).filter(Role.name == "professor").first()
        if not professor:
            professor = Role(
                name="professor",
                description="Professor",
                is_system_role=True
            )
            self.db.add(professor)
            self.db.flush()
            
            professor_permissions = self.db.query(Permission).filter(
                Permission.name.in_([
                    "alunos:read",
                    "turmas:read",
                    "notas:create", "notas:read", "notas:update",
                    "presencas:create", "presencas:read", "presencas:update",
                    "horarios:read"
                ])
            ).all()
            professor.permissions.extend(professor_permissions)
        
        # 4. Secretário - gerenciar matrículas e financeiro
        secretario = self.db.query(Role).filter(Role.name == "secretario").first()
        if not secretario:
            secretario = Role(
                name="secretario",
                description="Secretário escolar",
                is_system_role=True
            )
            self.db.add(secretario)
            self.db.flush()
            
            secretario_permissions = self.db.query(Permission).filter(
                Permission.name.in_([
                    "alunos:create", "alunos:read", "alunos:update",
                    "turmas:read",
                    "mensalidades:create", "mensalidades:read", "mensalidades:update",
                    "relatorios:read"
                ])
            ).all()
            secretario.permissions.extend(secretario_permissions)
        
        # 5. Responsável - apenas visualização
        responsavel = self.db.query(Role).filter(Role.name == "responsavel").first()
        if not responsavel:
            responsavel = Role(
                name="responsavel",
                description="Responsável/Encarregado de aluno",
                is_system_role=True
            )
            self.db.add(responsavel)
            self.db.flush()
            
            responsavel_permissions = self.db.query(Permission).filter(
                Permission.name.in_([
                    "alunos:read",
                    "notas:read",
                    "mensalidades:read",
                    "presencas:read"
                ])
            ).all()
            responsavel.permissions.extend(responsavel_permissions)
        
        self.db.commit()
    
    def user_has_permission(
        self,
        user: Usuario,
        resource: str,
        action: str,
        target_escola_id: Optional[int] = None
    ) -> bool:
        """Verificar se usuário tem permissão"""
        
        # Superadmin sempre tem acesso
        if user.role.name == "superadmin":
            return True
        
        # Verificar isolamento de escola
        if target_escola_id and user.escola_id != target_escola_id:
            return False
        
        # Buscar permissão
        permission_name = f"{resource}:{action}"
        
        for permission in user.role.permissions:
            if permission.name == permission_name:
                return True
        
        return False

def require_permission(resource: str, action: str):
    """Decorator para verificar permissão"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            # Extrair current_user e db dos kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: user/db não fornecidos"
                )
            
            permission_service = PermissionService(db)
            
            # Verificar permissão
            if not permission_service.user_has_permission(current_user, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Sem permissão para {action} em {resource}"
                )
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro interno: user/db não fornecidos"
                )
            
            permission_service = PermissionService(db)
            
            if not permission_service.user_has_permission(current_user, resource, action):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Sem permissão para {action} em {resource}"
                )
            
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
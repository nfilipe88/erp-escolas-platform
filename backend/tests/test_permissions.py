# backend/tests/test_permissions.py - TESTES DE PERMISSÕES
import pytest
from fastapi import status
from app.core.permissions import PermissionService, ResourceEnum, ActionEnum

class TestPermissions:
    """Testes do sistema de permissões"""
    
    def test_create_default_permissions(self, db):
        """Teste de criação de permissões padrão"""
        service = PermissionService(db)
        service.create_default_permissions()
        
        from app.models.permission import Permission
        permissions = db.query(Permission).all()
        
        assert len(permissions) > 0
        assert any(p.name == "alunos:create" for p in permissions)
        assert any(p.name == "notas:read" for p in permissions)
    
    def test_create_default_roles(self, db):
        """Teste de criação de roles padrão"""
        service = PermissionService(db)
        service.create_default_permissions()
        service.create_default_roles()
        
        from app.models.permission import Role
        roles = db.query(Role).all()
        
        assert len(roles) >= 5
        role_names = [r.name for r in roles]
        assert "superadmin" in role_names
        assert "admin_escola" in role_names
        assert "professor" in role_names
    
    def test_user_has_permission_superadmin(self, db, admin_user):
        """Teste de permissão de superadmin"""
        # Atualizar role para superadmin
        from app.models.permission import Role
        superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
        admin_user.role_id = superadmin_role.id
        db.commit()
        
        service = PermissionService(db)
        
        # Superadmin tem todas as permissões
        assert service.user_has_permission(
            admin_user, 
            ResourceEnum.ALUNOS, 
            ActionEnum.CREATE
        ) is True
        assert service.user_has_permission(
            admin_user,
            ResourceEnum.CONFIGURACOES,
            ActionEnum.UPDATE
        ) is True
    
    def test_user_without_permission(self, db):
        """Teste de usuário sem permissão"""
        from app.models.usuario import Usuario
        from app.models.permission import Role
        
        # Criar role sem permissões
        role = Role(name="test_role", description="Teste")
        db.add(role)
        db.commit()
        
        # Criar usuário com essa role
        user = Usuario(
            nome="Teste",
            email="teste@teste.com",
            senha_hash="hash",
            role_id=role.id,
            ativo=True
        )
        db.add(user)
        db.commit()
        
        service = PermissionService(db)
        
        # Usuário não tem permissão
        assert service.user_has_permission(
            user,
            ResourceEnum.ALUNOS,
            ActionEnum.CREATE
        ) is False
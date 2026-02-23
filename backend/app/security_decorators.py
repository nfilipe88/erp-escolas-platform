"""
🔐 SECURITY DECORATORS - MULTI-TENANT SAAS
Funções e dependências para garantir isolamento de dados entre escolas.
"""
from fastapi import Depends, HTTPException, status
from typing import Optional, List

from app.models import usuario as models_user
from app.security import get_current_user

# Funções auxiliares
def has_role(user: models_user.Usuario, role_name: str) -> bool:
    """Verifica se o utilizador tem uma role específica."""
    return any(role.name == role_name for role in user.roles)

def has_any_role(user: models_user.Usuario, role_names: List[str]) -> bool:
    """Verifica se o utilizador tem pelo menos uma das roles."""
    return any(role.name in role_names for role in user.roles)

# ==============================================================================
# DEPENDÊNCIAS PRINCIPAIS (para usar com Depends())
# ==============================================================================

def get_current_escola_id(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> Optional[int]:
    """
    Retorna o ID da escola do utilizador autenticado.
    
    - Superadmin → None (sem filtro, vê tudo)
    - Outros perfis → escola_id do utilizador
    - Sem escola → HTTP 403
    """
    if has_role(current_user, "superadmin"):
        return None
    
    if not current_user.escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilizador não está associado a nenhuma escola."
        )
    return current_user.escola_id

def require_escola_id(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> int:
    """
    EXIGE que o utilizador tenha escola associada e retorna o ID.
    
    - Superadmin → HTTP 400 (deve usar rotas explícitas)
    - Outros → escola_id ou HTTP 400
    """
    if has_role(current_user, "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar a escola explicitamente."
        )
    
    if not current_user.escola_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador não está associado a nenhuma escola."
        )
    return current_user.escola_id

# ==============================================================================
# DEPENDÊNCIAS DE PERFIL
# ==============================================================================

async def superadmin_required(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> models_user.Usuario:
    """Permite acesso APENAS a superadmin."""
    if not has_role(current_user, "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas superadmin."
        )
    return current_user

async def admin_or_superadmin_required(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> models_user.Usuario:
    """Permite acesso a admin (diretor) e superadmin."""
    if not has_any_role(current_user, ["admin", "superadmin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )
    return current_user

# ==============================================================================
# FUNÇÕES AUXILIARES DE VALIDAÇÃO
# ==============================================================================

def verify_school_access(
    escola_id: int,
    current_user: models_user.Usuario
) -> None:
    """
    Verifica se o utilizador tem acesso à escola especificada.
    
    - Superadmin: acesso total
    - Outros: apenas se escola_id == current_user.escola_id
    """
    if has_role(current_user, "superadmin"):
        return
    
    if current_user.escola_id != escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Não tem permissão para aceder dados da escola {escola_id}."
        )

def verify_resource_ownership(
    resource_escola_id: int,
    current_user: models_user.Usuario,
    resource_name: str = "recurso"
) -> None:
    """
    Verifica se um recurso pertence à escola do utilizador.
    
    - Superadmin: sempre autorizado
    - Outros: falha se resource_escola_id != current_user.escola_id
    """
    if has_role(current_user, "superadmin"):
        return
    
    if current_user.escola_id != resource_escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Este {resource_name} não pertence à sua escola."
        )

def can_modify_user(
    target_user: models_user.Usuario,
    current_user: models_user.Usuario
) -> None:
    """
    Verifica se o utilizador atual pode modificar outro utilizador.
    
    REGRAS:
    - Superadmin: pode modificar qualquer um
    - Admin da escola: pode modificar utilizadores da mesma escola,
      EXCETO outros admins ou superadmins
    - Outros perfis: proibido
    """
    # Superadmin pode tudo
    if has_role(current_user, "superadmin"):
        return
    
    # Admin da escola
    if has_role(current_user, "admin"):
        if target_user.escola_id != current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Só pode modificar utilizadores da sua escola."
            )
        if has_any_role(target_user, ["admin", "superadmin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não pode modificar administradores ou superadmins."
            )
        return
    
    # Qualquer outro perfil
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Não tem permissão para modificar utilizadores."
    )

# ==============================================================================
# UTILITÁRIO: DETERMINAR ESCOLA DESTINO EM CRIAÇÕES
# ==============================================================================

def get_target_escola_id(
    current_user: models_user.Usuario,
    payload_escola_id: Optional[int] = None,
    resource_type: str = "recurso"
) -> int:
    """
    Determina qual escola_id usar na criação de recursos.
    
    LÓGICA:
    - Superadmin: DEVE fornecer escola_id no payload (obrigatório)
    - Outros perfis: USA automaticamente current_user.escola_id
    
    Returns:
        int: ID da escola destino
    
    Raises:
        HTTPException: Se superadmin não forneceu escola_id OU
                       se utilizador não tem escola associada
    """
    if has_role(current_user, "superadmin"):
        if not payload_escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Superadmin deve informar 'escola_id' ao criar {resource_type}."
            )
        return payload_escola_id
    else:
        if not current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador não está associado a nenhuma escola."
            )
        return current_user.escola_id

# ==============================================================================
# PERMISSÕES BASEADAS EM PERMISSÕES GRANULARES
# ==============================================================================

def check_permission(required_permissions: List[str]):
    """
    Decorator para verificar se o utilizador atual tem as permissões necessárias.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Utilizador não autenticado."
                )
            # Superadmin passa sempre
            if has_role(current_user, "superadmin"):
                return func(*args, **kwargs)
            
            # Verificar permissões nas roles
            user_permissions = set()
            for role in current_user.roles:
                for perm in role.permissions:
                    perm_name = getattr(perm, 'name', getattr(perm, 'nome', '')).lower()
                    user_permissions.add(perm_name)
            
            # Verificar se tem todas as permissões exigidas (ou pelo menos uma, dependendo da lógica)
            if not any(p in user_permissions for p in required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Não tem permissões suficientes para realizar esta ação."
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_permissions(required_permissions: List[str]):
    """
    Dependência para verificar permissões.
    Uso: def endpoint(..., permissao=Depends(require_permissions(["criar_usuario"]))):
    """
    def permission_checker(current_user: models_user.Usuario = Depends(get_current_user)):
        # Superadmin passa sempre
        if has_role(current_user, "superadmin"):
            return current_user
        
        # Obter todas as permissões do utilizador
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                perm_name = getattr(perm, 'name', getattr(perm, 'nome', '')).lower()
                user_permissions.add(perm_name)
        
        # Verificar se tem pelo menos uma das permissões necessárias
        if not any(p in user_permissions for p in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Não tem permissões suficientes para realizar esta ação."
            )
        return current_user
    return permission_checker
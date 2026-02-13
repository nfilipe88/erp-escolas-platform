"""
🔐 SECURITY DECORATORS - MULTI-TENANT SAAS
Funções e dependências para garantir isolamento de dados entre escolas.

REGRAS DE OURO:
1. NUNCA confiar em escola_id vindo do payload
2. SEMPRE validar ownership antes de retornar dados
3. Superadmin = acesso total, outros = apenas própria escola
"""
from fastapi import Depends, HTTPException, status
from typing import Optional

from app.models import usuario as models_user
from app.security import get_current_user


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
    
    USO: Filtros em listagens (GET /recursos)
    """
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        return None
    
    if not current_user.escola_id:  # type: ignore[truthy-function]
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
    
    USO: Rotas "minha-escola" (ex: /configuracoes)
    """
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar a escola explicitamente."
        )
    
    if not current_user.escola_id:  # type: ignore[truthy-function]
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
    if current_user.perfil != "superadmin":  # type: ignore[comparison-overlap]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas superadmin."
        )
    return current_user


async def admin_or_superadmin_required(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> models_user.Usuario:
    """Permite acesso a admin (diretor) e superadmin."""
    if current_user.perfil not in ["admin", "superadmin"]:  # type: ignore[comparison-overlap]
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
    
    Lança HTTPException se não autorizado.
    """
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        return
    
    if current_user.escola_id != escola_id:  # type: ignore[comparison-overlap]
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
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        return
    
    if current_user.escola_id != resource_escola_id:  # type: ignore[comparison-overlap]
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
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        return
    
    # Admin da escola
    if current_user.perfil == "admin":  # type: ignore[comparison-overlap]
        if target_user.escola_id != current_user.escola_id:  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Só pode modificar utilizadores da sua escola."
            )
        if target_user.perfil in ["admin", "superadmin"]:  # type: ignore[comparison-overlap]
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
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        if not payload_escola_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Superadmin deve informar 'escola_id' ao criar {resource_type}."
            )
        return payload_escola_id
    else:
        if not current_user.escola_id:  # type: ignore[truthy-function]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Utilizador não está associado a nenhuma escola."
            )
        return current_user.escola_id
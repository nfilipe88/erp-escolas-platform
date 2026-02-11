"""
Decorators de Segurança para Isolamento Multi-tenant (SaaS)
Garante que usuários só acessam dados da própria escola
"""
from functools import wraps
from fastapi import HTTPException, status
from typing import Callable
from fastapi import Depends, HTTPException, status
from app.models import usuario as models_user
from app.security import get_current_user

# Retorna o ID da escola para filtrar queries (ou None se for superadmin)
def get_current_escola_id(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> int | None:
    if current_user.perfil == "superadmin":
        return None
    
    if not current_user.escola_id:
        # Segurança: Utilizador sem escola não deve ver nada
        # Podes optar por lançar erro ou retornar um ID impossível (-1)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Utilizador não está associado a nenhuma escola."
        )
    
    return current_user.escola_id

# Retorna o ID da escola OBRIGATÓRIO (para criação de dados)
def require_escola_id(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> int:
    if current_user.perfil == "superadmin":
        # Nota: Superadmins devem enviar o escola_id no corpo do request se quiserem criar algo específico
        # Mas aqui, para simplificar, vamos lançar erro se não houver contexto
        # O ideal seria verificar se o request body tem escola_id, mas isso é complexo em dependências.
        # Por agora, assumimos que superadmin deve agir como admin de uma escola se tiver escola_id,
        # ou precisas de lógica extra no router.
        pass 

    if not current_user.escola_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="É necessário estar associado a uma escola para realizar esta ação."
        )
    return current_user.escola_id



def require_superadmin(func: Callable) -> Callable:
    """
    Decorator: Permite acesso apenas para superadmin
    
    Uso:
        @require_superadmin
        def minha_funcao(current_user: Usuario = Depends(get_current_user)):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Procurar current_user nos kwargs
        current_user = kwargs.get('current_user')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno: current_user não encontrado"
            )
        
        if current_user.perfil != "superadmin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Apenas superadmin pode executar esta ação."
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_admin_or_superadmin(func: Callable) -> Callable:
    """
    Decorator: Permite acesso para admin da escola ou superadmin
    
    Uso:
        @require_admin_or_superadmin
        def minha_funcao(current_user: Usuario = Depends(get_current_user)):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno: current_user não encontrado"
            )
        
        if current_user.perfil not in ["admin", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Apenas administradores podem executar esta ação."
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def verify_school_access(escola_id: int, current_user: models_user.Usuario) -> None:
    """
    Função Helper: Verifica se o usuário tem acesso à escola
    
    Regras:
    - Superadmin: Acesso total
    - Admin/Professor/Secretaria: Apenas sua escola
    
    Lança HTTPException se não autorizado
    
    Args:
        escola_id: ID da escola a ser acessada
        current_user: Usuário logado
        
    Raises:
        HTTPException: Se acesso negado
    """
    # Superadmin tem acesso total
    if current_user.perfil == "superadmin":
        return
    
    # Outros perfis só acessam sua própria escola
    if current_user.escola_id != escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Você não tem permissão para acessar dados da escola {escola_id}."
        )


def verify_resource_ownership(
    resource_escola_id: int,
    current_user: models_user.Usuario,
    resource_name: str = "recurso"
) -> None:
    """
    Função Helper: Verifica se um recurso pertence à escola do usuário
    
    Args:
        resource_escola_id: ID da escola do recurso (aluno, turma, etc)
        current_user: Usuário logado
        resource_name: Nome do recurso (para mensagem de erro)
    
    Raises:
        HTTPException: Se o recurso não pertence à escola do usuário
    """
    if current_user.perfil == "superadmin":
        return
    
    if current_user.escola_id != resource_escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Este {resource_name} não pertence à sua escola."
        )


def require_same_school_or_superadmin(
    target_escola_id: int,
    current_user: models_user.Usuario
) -> None:
    """
    Valida se o usuário está acessando dados da própria escola
    ou se é superadmin (que pode acessar tudo)
    
    Args:
        target_escola_id: ID da escola alvo
        current_user: Usuário autenticado
        
    Raises:
        HTTPException: Se não autorizado
    """
    # Superadmin bypassa verificação
    if current_user.perfil == "superadmin":
        return
    
    # Usuário deve ter escola_id definida
    if not current_user.escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta não está associada a nenhuma escola."
        )
    
    # Verificar se é a mesma escola
    if current_user.escola_id != target_escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você só pode acessar dados da sua escola."
        )


def can_modify_user(target_user: models_user.Usuario, current_user: models_user.Usuario) -> None:
    """
    Verifica se o usuário atual pode modificar outro usuário
    
    Regras:
    - Superadmin pode modificar qualquer um
    - Admin pode modificar usuários da sua escola (exceto outros admins/superadmins)
    - Outros perfis não podem modificar ninguém
    
    Args:
        target_user: Usuário que será modificado
        current_user: Usuário que está tentando modificar
        
    Raises:
        HTTPException: Se não autorizado
    """
    # Superadmin pode tudo
    if current_user.perfil == "superadmin":
        return
    
    # Admin só pode modificar usuários da mesma escola
    if current_user.perfil == "admin":
        if target_user.escola_id != current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode modificar usuários da sua escola."
            )
        
        # Admin não pode modificar outro admin ou superadmin
        if target_user.perfil in ["admin", "superadmin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode modificar administradores ou superadmins."
            )
        
        return
    
    # Outros perfis não podem modificar ninguém
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Você não tem permissão para modificar usuários."
    )
"""
Decorators e Dependências de Segurança para Isolamento Multi‑tenant (SaaS)
Garante que utilizadores acedam apenas dados da sua própria escola.
"""
from fastapi import Depends, HTTPException, status
from typing import Optional

from app.models import usuario as models_user
from app.security import get_current_user


# ----------------------------------------------------------------------
# DEPENDÊNCIAS PRINCIPAIS (para usar com Depends())
# ----------------------------------------------------------------------

def get_current_escola_id(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> Optional[int]:
    """
    Retorna o ID da escola do utilizador autenticado.
    - Superadmin → retorna `None` (significa "sem filtro", vê tudo).
    - Outros perfis → retorna o `escola_id` do utilizador.
    - Utilizador sem escola associada → HTTP 403.

    Uso típico: filtros em listagens (GET /recursos).
    """
    if current_user.perfil == "superadmin":
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
    Exige que o utilizador tenha uma escola associada e retorna o ID.
    - Superadmin **não pode** usar esta dependência (lança 400).
    - Outros perfis: retorna `escola_id` ou lança 400 se não tiver.

    Uso típico: rotas "minha-escola" (ex: /minha-escola/configuracoes),
    onde a escola é implícita e o superadmin deve usar rotas explícitas.
    """
    if current_user.perfil == "superadmin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Superadmin deve especificar a escola explicitamente na requisição."
        )

    if not current_user.escola_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilizador não está associado a nenhuma escola."
        )
    return current_user.escola_id


# ----------------------------------------------------------------------
# DEPENDÊNCIAS DE PERFIL (alternativa aos decoradores removidos)
# ----------------------------------------------------------------------

async def superadmin_required(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> models_user.Usuario:
    """Permite acesso apenas a superadmin."""
    if current_user.perfil != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas superadmin pode executar esta ação."
        )
    return current_user


async def admin_or_superadmin_required(
    current_user: models_user.Usuario = Depends(get_current_user)
) -> models_user.Usuario:
    """Permite acesso a administradores (admin da escola) e superadmin."""
    if current_user.perfil not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores ou superadmin podem executar esta ação."
        )
    return current_user


# ----------------------------------------------------------------------
# FUNÇÕES AUXILIARES (para validação dentro de endpoints/CRUDs)
# ----------------------------------------------------------------------

def verify_school_access(
    escola_id: int,
    current_user: models_user.Usuario
) -> None:
    """
    Verifica se o utilizador tem acesso à escola especificada.
    - Superadmin: acesso total.
    - Outros perfis: apenas se `escola_id == current_user.escola_id`.

    Lança HTTPException se não autorizado.
    """
    if current_user.perfil == "superadmin":
        return

    if current_user.escola_id != escola_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado. Você não tem permissão para aceder dados da escola {escola_id}."
        )


def verify_resource_ownership(
    resource_escola_id: int,
    current_user: models_user.Usuario,
    resource_name: str = "recurso"
) -> None:
    """
    Verifica se um recurso pertence à escola do utilizador.
    - Superadmin: sempre autorizado.
    - Outros perfis: falha se `resource_escola_id != current_user.escola_id`.
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
    Valida que o utilizador está a aceder à sua própria escola ou é superadmin.
    Equivalente a `verify_school_access`.
    """
    verify_school_access(target_escola_id, current_user)


def can_modify_user(
    target_user: models_user.Usuario,
    current_user: models_user.Usuario
) -> None:
    """
    Verifica se o utilizador atual pode modificar outro utilizador.

    Regras:
    - Superadmin: pode modificar qualquer um.
    - Admin da escola: pode modificar utilizadores da mesma escola,
        exceto outros administradores ou superadmins.
    - Outros perfis: proibido.
    """
    # Superadmin pode tudo
    if current_user.perfil == "superadmin":
        return

    # Admin da escola
    if current_user.perfil == "admin":
        if target_user.escola_id != current_user.escola_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Só pode modificar utilizadores da sua escola."
            )
        if target_user.perfil in ["admin", "superadmin"]:
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
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user, get_password_hash, verify_password
from app.schemas import schema_usuario as schemas_user
from app.cruds import crud_usuario, crud_escola
from app.models import usuario as models_user
from app.security_decorators import (
    get_current_escola_id,
    require_escola_id,
    superadmin_required,
    admin_or_superadmin_required,
    can_modify_user
)

router = APIRouter(tags=["Usuários"])

@router.post("/usuarios", response_model=schemas_user.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    usuario: schemas_user.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # Superadmin: pode criar qualquer perfil, com ou sem escola
    if current_user.perfil == "superadmin":  # type: ignore[comparison-overlap]
        escola_destino_id = usuario.escola_id  # pode ser None (superadmin)
        if usuario.perfil != "superadmin" and not escola_destino_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Superadmin deve informar escola_id para perfis não‑superadmin."
            )
    else:
        # Admin pode criar apenas na sua escola
        if current_user.perfil != "admin":  # type: ignore[comparison-overlap]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas admin ou superadmin podem criar utilizadores."
            )
        escola_destino_id = current_user.escola_id
        if not escola_destino_id:  # type: ignore[truthy-function]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin sem escola associada."
            )
        if usuario.perfil in ["superadmin", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin não pode criar outro admin ou superadmin."
            )

    # Verificar se escola existe (se fornecida)
    if escola_destino_id:
        escola = crud_escola.get_escolas(db, skip=0, limit=1).filter_by(id=escola_destino_id).first()
        if not escola:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escola não encontrada")

    return crud_usuario.create_usuario(db=db, usuario=usuario, escola_id=escola_destino_id)

@router.get("/usuarios", response_model=List[schemas_user.UsuarioResponse])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_usuario.get_usuarios(db, skip, limit, escola_id=escola_id)

@router.get("/usuarios/professores", response_model=List[schemas_user.UsuarioResponse])
def listar_professores(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    return db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == escola_id,
        models_user.Usuario.perfil == "professor",  # type: ignore[comparison-overlap]
        models_user.Usuario.ativo == True  # type: ignore[comparison-overlap]
    ).all()

@router.get("/meus-dados", response_model=schemas_user.UsuarioResponse)
def meus_dados(
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return current_user

@router.put("/meus-dados/alterar-senha")
def alterar_minha_senha(
    dados: schemas_user.SenhaUpdate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    if not verify_password(dados.senha_atual, str(current_user.senha_hash)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A senha atual está incorreta.")
    current_user.senha_hash = get_password_hash(dados.nova_senha)  # type: ignore[assignment]
    db.commit()
    return {"mensagem": "Senha alterada com sucesso"}

# Endpoints para administração de usuários (admin/superadmin)
@router.put("/usuarios/{usuario_id}")
def atualizar_usuario(
    usuario_id: int,
    dados: schemas_user.UsuarioCreate,  # Idealmente UsuarioUpdate, mas simplificado
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(admin_or_superadmin_required)
):
    target_user = db.query(models_user.Usuario).filter(models_user.Usuario.id == usuario_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    can_modify_user(target_user, current_user)
    # Atualizar campos (exemplo)
    target_user.nome = dados.nome
    target_user.email = dados.email
    target_user.ativo = dados.ativo
    if dados.perfil:
        target_user.perfil = dados.perfil.value  # type: ignore[assignment]
    if dados.senha:
        target_user.senha_hash = get_password_hash(dados.senha)  # type: ignore[assignment]
    db.commit()
    db.refresh(target_user)
    return target_user

@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(superadmin_required)
):
    """Apenas superadmin pode remover usuários."""
    user = db.query(models_user.Usuario).filter(models_user.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    db.delete(user)
    db.commit()
    return None
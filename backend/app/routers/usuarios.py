from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2 import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.cruds import crud_usuario, crud_escola, crud_notificacao
from app.schemas import schema_notificacao
from app.schemas import schema_usuario as schemas_user
from app.models import usuario as models_user
from app.models.role import Role
from app.models import escola as models_escola
from app.security import get_current_user, get_password_hash, verify_password
from app.security_decorators import (
    get_current_escola_id, require_escola_id, superadmin_required, admin_or_superadmin_required,
    can_modify_user, has_role, require_permissions
)

router = APIRouter(tags=["Usuários"])

@router.post("/", response_model=schemas_user.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(
    usuario: schemas_user.UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(require_permissions(["criar_usuarios"]))
):
    # 1. Verificar permissão: apenas superadmin ou admin
    if not (has_role(current_user, "superadmin") or has_role(current_user, "admin")):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas admin ou superadmin podem criar utilizadores."
        )

    # 2. Determinar escola destino
    if has_role(current_user, "superadmin"):
        escola_destino_id = usuario.escola_id  # pode ser None (superadmin criando outro superadmin)
    else:  # admin
        escola_destino_id = current_user.escola_id
        if not escola_destino_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin sem escola associada."
            )

    # 3. Se for admin, não pode criar outro admin ou superadmin
    if has_role(current_user, "admin"):
        # Buscar as roles selecionadas
        roles_selecionadas = db.query(Role).filter(Role.id.in_(usuario.roles)).all()
        nomes_proibidos = ["superadmin", "admin"]
        for role in roles_selecionadas:
            if role.name in nomes_proibidos:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin não pode criar outro admin ou superadmin."
                )

    # 4. Verificar se escola existe (se fornecida)
    if escola_destino_id:
        escola = db.query(models_escola.Escola).filter(models_escola.Escola.id == escola_destino_id).first()
        if not escola:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escola não encontrada")

    # 5. Criar usuário com as roles
    # return crud_usuario.create_usuario(
    #     db=db,
    #     usuario=usuario,
    #     escola_id=escola_destino_id,
    #     roles_ids=usuario.roles  # Passa a lista de IDs das roles
    # )
    try:
        return crud_usuario.create_usuario(
            db=db, 
            usuario=usuario, 
            roles_ids=usuario.roles 
        )
    except IntegrityError as e:
        # Revertemos a transação falhada
        db.rollback()
        # Se o erro na mensagem contiver a palavra 'email', sabemos que foi duplicação de email
        if "email" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este endereço de e-mail já está registado no sistema."
            )
        # Se for outro erro de integridade (ex: escola não existe)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro de integridade de dados. Verifique os campos submetidos."
        )

@router.get("/", response_model=List[schemas_user.UsuarioResponse])
def listar_usuarios(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    escola_id: Optional[int] = Depends(get_current_escola_id)
):
    return crud_usuario.get_usuarios(db, skip, limit, escola_id=escola_id)

@router.get("/professores", response_model=List[schemas_user.UsuarioResponse])
def listar_professores(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id),
    current_user: models_user.Usuario = Depends(require_permissions(["ver_professores"]))
):
    # Como procurar por uma Role dentro de um relacionamento Many-to-Many no SQLAlchemy:
    return db.query(models_user.Usuario).join(models_user.Usuario.roles).filter(
        models_user.Usuario.escola_id == escola_id,
        Role.name == "professor", # ← Forma correta de filtrar por um elemento do relacionamento
        models_user.Usuario.ativo == True
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
@router.put("/{usuario_id}")
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
    if dados.roles:
        target_user.roles = dados.roles.value  # type: ignore[assignment]
    if dados.senha:
        target_user.senha_hash = get_password_hash(dados.senha)  # type: ignore[assignment]
    db.commit()
    db.refresh(target_user)
    return target_user

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(require_permissions(["deletar_usuarios"]))
):
    """Apenas superadmin pode remover usuários."""
    user = db.query(models_user.Usuario).filter(models_user.Usuario.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilizador não encontrado")
    db.delete(user)
    db.commit()
    return None

@router.get("/me/notificacoes", response_model=list[schema_notificacao.NotificacaoResponse])
def minhas_notificacoes(
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_notificacao.listar_minhas_notificacoes(db, current_user.id)

# @router.get("/professores", response_model=List[schemas_user.UsuarioResponse])
# def listar_professores(
#     db: Session = Depends(get_db),
#     escola_id: int = Depends(require_escola_id)
# ):
#     return db.query(models_user.Usuario).join(models_user.Usuario.roles).filter(
#         models_user.Usuario.escola_id == escola_id,
#         Role.name == "professor",
#         models_user.Usuario.ativo == True
#     ).all()
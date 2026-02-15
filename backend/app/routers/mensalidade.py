from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models import usuario as models_user
from app.schemas import schema_mensalidade
from app.schemas import schema_notificacao
from app.cruds import crud_mensalidade
from app.cruds import crud_notificacao
from app.security import get_current_user
from app.security_decorators import check_permission 

# Email
from app.core.email import enviar_email_recibo

router = APIRouter(prefix="/mensalidades", tags=["Mensalidades"])

@router.post("/", response_model=schema_mensalidade.MensalidadeResponse)
@check_permission(["admin", "secretaria"]) # Só Admin e Secretaria criam cobranças
def criar_mensalidade(
    mensalidade: schema_mensalidade.MensalidadeCreate, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.create_mensalidade(db, mensalidade, current_user.escola_id)

@router.get("/aluno/{aluno_id}", response_model=List[schema_mensalidade.MensalidadeResponse])
@check_permission(["admin", "secretaria", "superadmin", "aluno"]) # Aluno também pode ver as suas
def listar_por_aluno(
    aluno_id: int, 
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    return crud_mensalidade.get_mensalidades_aluno(db, aluno_id)

# --- A ROTA MÁGICA: PAGAR COM EMAIL E NOTIFICAÇÃO ---
@router.put("/{id}/pagar")
@check_permission(["admin", "secretaria", "superadmin"]) # Apenas staff confirma pagamento
def pagar_mensalidade(
    id: int, 
    forma_pagamento: str,
    background_tasks: BackgroundTasks, # Injeção para tarefas em segundo plano
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # 1. Registar Pagamento
    mensalidade_paga = crud_mensalidade.registar_pagamento(db, id, forma_pagamento)
    
    if not mensalidade_paga:
        raise HTTPException(status_code=400, detail="Erro ao processar pagamento.")

    # 2. Dados do Aluno
    aluno = mensalidade_paga.aluno
    destinatario_email = getattr(aluno, "email", None)
    
    # 3. Enviar Email (Background Task - Não bloqueia o request)
    if destinatario_email:
        background_tasks.add_task(
            enviar_email_recibo,
            destinatario=destinatario_email,
            aluno_nome=aluno.nome,
            valor=mensalidade_paga.valor_base,
            mes=mensalidade_paga.descricao or "Mensalidade"
        )

    # 4. Criar Notificação Interna (Sininho)
    # Tenta encontrar o utilizador associado a este aluno (pelo email)
    if destinatario_email:
        user_db = db.query(models_user.Usuario).filter(models_user.Usuario.email == destinatario_email).first()
        
        if user_db:
            nova_notificacao = schema_notificacao.NotificacaoCreate(
                usuario_id=user_db.id,
                titulo="Pagamento Confirmado ✅",
                mensagem=f"O pagamento de {mensalidade_paga.valor_base} Kz referente a {mensalidade_paga.descricao} foi recebido."
            )
            crud_notificacao.criar_notificacao(db, nova_notificacao)

    return mensalidade_paga
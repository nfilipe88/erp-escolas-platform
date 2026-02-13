# No main.py

# 1. Adicionar importações no topo
from fastapi import BackgroundTasks, APIRouter, Depends, HTTPException, status
from app.core.email import enviar_email_recibo
from typing import List, Optional

from app.db.database import get_db
from app.security import get_current_user
from app.schemas import schema_aluno as schemas_aluno
from app.schemas import schema_boletim as schemas_boletim
from app.cruds import crud_mensalidade, crud_nota, crud_turma
from app.models import usuario as models_user
from app.security_decorators import (
    get_current_escola_id,
    verify_resource_ownership,
    admin_or_superadmin_required,
)

router = APIRouter(prefix="/mensalidades", tags=["Mensalidades"])
# ...

# 2. Atualizar a Rota de Pagamento
@router.put("/mensalidades/{id}/pagar")
def pagar_mensalidade(
    id: int, 
    forma_pagamento: str,
    background_tasks: BackgroundTasks, # <--- Injeção de Dependência Mágica
    db: Session = Depends(get_db),
    current_user: models_user.Usuario = Depends(get_current_user)
):
    # 1. Processar o pagamento no banco de dados
    mensalidade_paga = crud_mensalidade.registar_pagamento(db, id, forma_pagamento)
    
    if not mensalidade_paga:
        raise HTTPException(status_code=400, detail="Erro ao processar pagamento")

    # 2. Buscar dados do aluno para enviar o email
    # (Precisamos do email do aluno ou encarregado. Vamos assumir que está em mensalidade_paga.aluno.email)
    aluno = mensalidade_paga.aluno
    
    if aluno and aluno.email: # Verifica se o aluno tem email registado
        # 3. Agendar o envio do email em segundo plano
        background_tasks.add_task(
            enviar_email_recibo,
            destinatario=aluno.email,
            aluno_nome=aluno.nome,
            valor=mensalidade_paga.valor_base,
            mes=mensalidade_paga.descricao
        )
    
    return mensalidade_paga
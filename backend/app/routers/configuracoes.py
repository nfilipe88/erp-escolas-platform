from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas import schema_configuracao as schemas_config
from app.cruds import crud_configuracao
# Importa a nova dependência
from backend.app.security_decorattors import get_current_escola_id, require_escola_id

@router.get("/minha-escola/configuracoes")
def ler_config(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id) # Obriga a ter escola
):
    # O CRUD usa este ID. Impossível ver config de outros.
    config = crud_configuracao.get_config_by_escola(db, escola_id)
    if not config:
        # Se não existir, cria uma default automaticamente (UX melhor)
        return crud_configuracao.create_default_config(db, escola_id)
    return config
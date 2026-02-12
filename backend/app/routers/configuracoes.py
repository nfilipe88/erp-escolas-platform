from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import schema_configuracao as schemas_config
from app.cruds import crud_configuracao
from app.security_decorators import require_escola_id
from app.models.configuracao import Configuracao

router = APIRouter(prefix="/escolas", tags=["Configurações"])

@router.get("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def ler_config(
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    config = crud_configuracao.get_config_by_escola(db, escola_id)
    if not config:
        # Criar configuração padrão
        config = Configuracao(escola_id=escola_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config

@router.put("/minha-escola/configuracoes", response_model=schemas_config.ConfiguracaoResponse)
def atualizar_config(
    dados: schemas_config.ConfiguracaoUpdate,
    db: Session = Depends(get_db),
    escola_id: int = Depends(require_escola_id)
):
    return crud_configuracao.update_config(db, escola_id, dados)
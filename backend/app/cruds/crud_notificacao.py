from sqlalchemy.orm import Session
from app.models import notificacao as models
from app.schemas import schema_notificacao as schemas

def criar_notificacao(db: Session, notificacao: schemas.NotificacaoCreate):
    db_obj = models.Notificacao(**notificacao.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def listar_minhas_notificacoes(db: Session, usuario_id: int):
    return db.query(models.Notificacao).filter(
        models.Notificacao.usuario_id == usuario_id
    ).order_by(models.Notificacao.data_criacao.desc()).all()
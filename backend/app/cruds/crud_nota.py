# backend/app/cruds/crud_nota.py
from sqlalchemy.orm import Session
from app.models import nota as models
from app.schemas import nota as schemas

def lancar_nota(db: Session, nota: schemas.NotaCreate):
    # Verifica se já existe nota (mesmo aluno, disciplina, trimestre e descrição)
    nota_existente = db.query(models.Nota).filter(
        models.Nota.aluno_id == nota.aluno_id,
        models.Nota.disciplina_id == nota.disciplina_id,
        models.Nota.trimestre == nota.trimestre,
        models.Nota.descricao == nota.descricao
    ).first()

    if nota_existente:
        # ATUALIZA
        nota_existente.valor = nota.valor # type: ignore
        # Só atualiza o arquivo se vier um novo. Se não, mantém o antigo.
        if nota.arquivo_url:
             nota_existente.arquivo_url = nota.arquivo_url # type: ignore
             
        db.commit()
        db.refresh(nota_existente)
        return nota_existente
    else:
        # CRIA
        # O model_dump converte o schema para dicionário, incluindo o arquivo_url
        db_nota = models.Nota(**nota.model_dump())
        db.add(db_nota)
        db.commit()
        db.refresh(db_nota)
        return db_nota

def get_notas_by_disciplina(db: Session, disciplina_id: int):
    return db.query(models.Nota).filter(models.Nota.disciplina_id == disciplina_id).all()
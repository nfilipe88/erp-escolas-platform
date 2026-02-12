# app/cruds/crud_ponto.py
from sqlalchemy.orm import Session
from app.models import ponto_professor as models
from app.models import usuario as models_user
from datetime import date

def get_ponto_dia(db: Session, escola_id: int, data_ref: date):
    professores = db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == escola_id,
        models_user.Usuario.perfil == 'professor',
        models_user.Usuario.ativo == True
    ).all()

    registos = db.query(models.PontoProfessor).filter(
        models.PontoProfessor.escola_id == escola_id,
        models.PontoProfessor.data == data_ref
    ).all()
    registo_dict = {r.professor_id: r for r in registos}

    resultado = []
    for prof in professores:
        r = registo_dict.get(prof.id)
        resultado.append({
            "professor_id": prof.id,
            "professor_nome": prof.nome,
            "presente": r.presente if r else True,
            "observacao": r.observacao if r else "",
            "ja_registado": r is not None
        })
    return resultado

def salvar_ponto(db: Session, escola_id: int, dados_lista: list, data_ref: date):
    db.query(models.PontoProfessor).filter(
        models.PontoProfessor.escola_id == escola_id,
        models.PontoProfessor.data == data_ref
    ).delete()

    novos = []
    for item in dados_lista:
        novo = models.PontoProfessor(
            escola_id=escola_id,
            professor_id=item['professor_id'],
            data=data_ref,
            presente=item['presente'],
            observacao=item.get('observacao', '')
        )
        novos.append(novo)

    db.add_all(novos)
    db.commit()
    return {"msg": "Ponto dos professores atualizado com sucesso!"}
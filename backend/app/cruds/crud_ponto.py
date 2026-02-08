# app/cruds/crud_ponto.py
from sqlalchemy.orm import Session
from app.models import ponto_professor as models # Certifica-te que o model existe
from app.models import usuario as models_user
from datetime import date

def get_ponto_dia(db: Session, escola_id: int, data_ref: date):
    # 1. Busca todos os professores da escola
    professores = db.query(models_user.Usuario).filter(
        models_user.Usuario.escola_id == escola_id,
        models_user.Usuario.perfil == 'professor',
        models_user.Usuario.ativo == True
    ).all()

    # 2. Busca os registos de ponto já feitos para hoje
    registos = db.query(models.PontoProfessor).filter(
        models.PontoProfessor.escola_id == escola_id,
        models.PontoProfessor.data == data_ref
    ).all()

    # 3. Mescla os dados (Quem não tem registo, assume-se Presente ou Pendente)
    resultado = []
    for prof in professores:
        registo = next((r for r in registos if r.professor_id == prof.id), None)
        resultado.append({
            "professor_id": prof.id,
            "professor_nome": prof.nome,
            "presente": registo.presente if registo else True, # Padrão: Presente
            "observacao": registo.observacao if registo else "",
            "ja_registado": registo is not None
        })
    
    return resultado

def salvar_ponto(db: Session, escola_id: int, dados_lista: list, data_ref: date):
    # Remove registos anteriores do dia (estratégia de substituição)
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
# app/cruds/crud_nota.py
from sqlalchemy.orm import Session
from app.models import nota as models
from app.models import aluno as models_aluno
from app.schemas import schema_nota
from typing import Optional

def lancar_nota(db: Session, nota: schema_nota.NotaCreate, escola_id: int):
    # escola_id é obrigatório e será inserido no modelo
    nota_data = nota.model_dump()
    nota_data["escola_id"] = escola_id

    nota_existente = db.query(models.Nota).filter(
        models.Nota.aluno_id == nota.aluno_id,
        models.Nota.disciplina_id == nota.disciplina_id,
        models.Nota.trimestre == nota.trimestre,
        models.Nota.descricao == nota.descricao
    ).first()

    if nota_existente:
        nota_existente.valor = nota.valor
        if nota.arquivo_url:
            nota_existente.arquivo_url = nota.arquivo_url
        db.commit()
        db.refresh(nota_existente)
        return nota_existente
    else:
        db_nota = models.Nota(**nota_data)
        db.add(db_nota)
        db.commit()
        db.refresh(db_nota)
        return db_nota

def get_notas_by_disciplina(db: Session, disciplina_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Nota).join(models_aluno.Aluno)
    if escola_id:
        query = query.filter(models_aluno.Aluno.escola_id == escola_id)
    return query.filter(models.Nota.disciplina_id == disciplina_id).all()

def get_boletim_aluno(db: Session, aluno_id: int, escola_id: Optional[int] = None):
    aluno = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.id == aluno_id)
    if escola_id:
        aluno = aluno.filter(models_aluno.Aluno.escola_id == escola_id)
    aluno = aluno.first()
    if not aluno:
        return None

    if not aluno.turma:
        return {
            "aluno_nome": aluno.nome,
            "aluno_bi": aluno.bi,
            "turma": "Sem Turma",
            "escola_id": aluno.escola_id,
            "linhas": []
        }

    disciplinas_turma = aluno.turma.disciplinas
    # Otimização: buscar todas as notas do aluno de uma vez
    todas_notas = db.query(models.Nota).filter(models.Nota.aluno_id == aluno_id).all()
    notas_por_disciplina = {}
    for nota in todas_notas:
        if nota.disciplina_id not in notas_por_disciplina:
            notas_por_disciplina[nota.disciplina_id] = []
        notas_por_disciplina[nota.disciplina_id].append(nota)

    linhas_boletim = []
    for disciplina in disciplinas_turma:
        notas_disciplina = notas_por_disciplina.get(disciplina.id, [])
        notas_por_trimestre = {}
        for nota in notas_disciplina:
            if nota.trimestre not in notas_por_trimestre:
                notas_por_trimestre[nota.trimestre] = []
            notas_por_trimestre[nota.trimestre].append(nota.valor)

        lista_notas_formatadas = []
        trimestres = ["1º Trimestre", "2º Trimestre", "3º Trimestre"]
        for trimestre in trimestres:
            valores = notas_por_trimestre.get(trimestre, [])
            if valores:
                media = sum(valores) / len(valores)
                lista_notas_formatadas.append({
                    "trimestre": trimestre,
                    "valor": round(media, 2),
                    "descricao": f"Média {trimestre}"
                })
            else:
                lista_notas_formatadas.append({
                    "trimestre": trimestre,
                    "valor": None,
                    "descricao": "Sem nota"
                })

        valores_com_notas = [n["valor"] for n in lista_notas_formatadas if n["valor"] is not None]
        media_provisoria = round(sum(valores_com_notas) / len(valores_com_notas), 2) if valores_com_notas else 0

        linhas_boletim.append({
            "disciplina": disciplina.nome,
            "notas": lista_notas_formatadas,
            "media_provisoria": media_provisoria
        })

    return {
        "aluno_nome": aluno.nome,
        "aluno_bi": aluno.bi,
        "turma": aluno.turma.nome,
        "escola_id": aluno.escola_id,
        "linhas": linhas_boletim
    }
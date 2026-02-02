# backend/app/cruds/crud_nota.py
from sqlalchemy.orm import Session
from app.models import nota as models
from app.models import aluno as models_aluno
from app.schemas import schema_nota
from app.schemas import schema_boletim

def lancar_nota(db: Session, nota: schema_nota.NotaCreate):
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

def get_boletim_aluno(db: Session, aluno_id: int):
    # Busca o aluno
    aluno = db.query(models_aluno.Aluno).filter(
        models_aluno.Aluno.id == aluno_id
    ).first()
    
    if not aluno:
        return None
    
    # Verifica se o aluno tem turma
    if not aluno.turma:
        return {
            "aluno_nome": aluno.nome,
            "aluno_bi": aluno.bi,
            "turma": "Sem Turma",
            "linhas": []
        }
    
    # Busca TODAS as disciplinas da turma do aluno
    # Não apenas as que têm notas
    disciplinas_turma = aluno.turma.disciplinas
    
    linhas_boletim = []
    
    for disciplina in disciplinas_turma:
        # Busca todas as notas desta disciplina para este aluno
        notas_disciplina = db.query(models.Nota).filter(
            models.Nota.aluno_id == aluno_id,
            models.Nota.disciplina_id == disciplina.id
        ).all()
        
        # Organiza as notas por trimestre
        notas_por_trimestre = {}
        for nota in notas_disciplina:
            if nota.trimestre not in notas_por_trimestre:
                notas_por_trimestre[nota.trimestre] = []
            notas_por_trimestre[nota.trimestre].append(nota.valor)
        
        # Cria a lista de notas no formato esperado
        lista_notas_formatadas = []
        
        # Definir trimestres padrão
        trimestres = ["1º Trimestre", "2º Trimestre", "3º Trimestre"]
        
        for trimestre in trimestres:
            valores_trimestre = notas_por_trimestre.get(trimestre, [])
            if valores_trimestre:
                # Se houver múltiplas notas no mesmo trimestre, calcula média
                media_trimestre = sum(valores_trimestre) / len(valores_trimestre)
                lista_notas_formatadas.append({
                    "trimestre": trimestre,
                    "valor": round(media_trimestre, 2),
                    "descricao": f"Média {trimestre}"
                })
            else:
                # Sem notas neste trimestre
                lista_notas_formatadas.append({
                    "trimestre": trimestre,
                    "valor": None,
                    "descricao": "Sem nota"
                })
        
        # Calcula a média geral das notas (apenas trimestres com notas)
        valores_com_notas = [n["valor"] for n in lista_notas_formatadas if n["valor"] is not None]
        media_provisoria = 0
        if valores_com_notas:
            media_provisoria = round(sum(valores_com_notas) / len(valores_com_notas), 2)
        
        linhas_boletim.append({
            "disciplina": disciplina.nome,
            "notas": lista_notas_formatadas,
            "media_provisoria": media_provisoria
        })
    
    return {
        "aluno_nome": aluno.nome,
        "aluno_bi": aluno.bi,
        "turma": aluno.turma.nome,
        "linhas": linhas_boletim
    }
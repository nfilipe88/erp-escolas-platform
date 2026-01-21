# backend/app/cruds/crud_nota.py
from sqlalchemy.orm import Session
from app.models import nota as models
from app.models import aluno as models_aluno
from app.schemas import nota as schemas
from app.schemas import boletim as schemas_boletim

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

def get_boletim_aluno(db: Session, aluno_id: int):
    # CORREÇÃO: Usa 'models_aluno.Aluno' em vez de 'models.Aluno'
    aluno = db.query(models_aluno.Aluno).filter(models_aluno.Aluno.id == aluno_id).first()
    
    if not aluno:
        return None

    notas = db.query(models.Nota).filter(models.Nota.aluno_id == aluno_id).all()

    # 3. Agrupar por Disciplina (Dicionário temporário)
    # Estrutura: { "Matemática": [Nota1, Nota2], "História": [Nota1] }
    dados_agrupados = {}
    
    for nota in notas:
        disc_nome = nota.disciplina.nome
        if disc_nome not in dados_agrupados:
            dados_agrupados[disc_nome] = []
        
        dados_agrupados[disc_nome].append({
            "trimestre": nota.trimestre,
            "valor": nota.valor,
            "descricao": nota.descricao
        })

    # 4. Construir a resposta final
    linhas_boletim = []
    for disc_nome, lista_notas in dados_agrupados.items():
        # Calcula média simples das notas lançadas
        soma = sum(n["valor"] for n in lista_notas)
        media = soma / len(lista_notas) if lista_notas else 0
        
        linhas_boletim.append({
            "disciplina": disc_nome,
            "notas": lista_notas,
            "media_provisoria": round(media, 1)
        })

    return {
        "aluno_nome": aluno.nome,
        "aluno_bi": aluno.bi,
        "turma": aluno.turma.nome if aluno.turma else "Sem Turma",
        "linhas": linhas_boletim
    }
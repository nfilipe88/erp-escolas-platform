# app/cruds/crud_aluno.py
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models import aluno as models
from app.models import nota as models_nota, disciplina as models_disciplina, turma as models_turma
from app.schemas import schema_aluno
from typing import Optional, List

def get_aluno(db: Session, aluno_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.id == aluno_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.first()

def get_alunos(db: Session, skip: int = 0, limit: int = 100, escola_id: Optional[int] = None):
    query = db.query(models.Aluno)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.offset(skip).limit(limit).all()

def get_alunos_por_turma(db: Session, turma_id: int, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.turma_id == turma_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.all()

def create_aluno(db: Session, aluno: schema_aluno.AlunoCreate, escola_id: int):
    db_aluno = models.Aluno(
        nome=aluno.nome,
        bi=aluno.bi,
        data_nascimento=aluno.data_nascimento,
        escola_id=escola_id,
        turma_id=aluno.turma_id,
        ativo=aluno.ativo
    )
    db.add(db_aluno)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def update_aluno(db: Session, aluno_id: int, aluno_update: schema_aluno.AlunoUpdate,
                 escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.id == aluno_id)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    db_aluno = query.first()
    if not db_aluno:
        return None
    update_data = aluno_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_aluno, key, value)
    db.commit()
    db.refresh(db_aluno)
    return db_aluno

def get_alunos_by_escola(db: Session, escola_id: int):
    return db.query(models.Aluno).filter(models.Aluno.escola_id == escola_id).all()

def get_aluno_by_bi(db: Session, bi: str, escola_id: Optional[int] = None):
    query = db.query(models.Aluno).filter(models.Aluno.bi == bi)
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    return query.first()

def get_alunos_com_relacoes(
    db: Session,
    escola_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Aluno]:
    """Buscar alunos com eager loading das relações"""
    
    query = db.query(models.Aluno).options(
        joinedload(models.Aluno.turma),  # JOIN para turma
        joinedload(models.Aluno.escola),  # JOIN para escola
        selectinload(models.Aluno.mensalidades),  # SELECT separado para mensalidades
        selectinload(models.Aluno.notas).joinedload(models_nota.Nota.disciplina)  # Notas + disciplinas
    )
    
    if escola_id:
        query = query.filter(models.Aluno.escola_id == escola_id)
    
    return query.offset(skip).limit(limit).all()

def get_boletim_aluno_otimizado(db: Session, aluno_id: int) -> dict:
    """Buscar boletim com queries otimizadas"""
    
    # 1. Buscar aluno com turma em uma query
    aluno = db.query(models.Aluno).options(
        joinedload(models.Aluno.turma).selectinload(models_turma.Turma.disciplinas)
    ).filter(models.Aluno.id == aluno_id).first()
    
    if not aluno or not aluno.turma:
        return None
    
    # 2. Buscar TODAS as notas do aluno em UMA query
    notas = db.query(models_nota.Nota).options(
        joinedload(models_nota.Nota.disciplina)
    ).filter(models_nota.Nota.aluno_id == aluno_id).all()
    
    # 3. Organizar em memória (zero queries adicionais)
    notas_por_disciplina = {}
    for nota in notas:
        if nota.disciplina_id not in notas_por_disciplina:
            notas_por_disciplina[nota.disciplina_id] = []
        notas_por_disciplina[nota.disciplina_id].append(nota)
    
    # 4. Construir resposta
    linhas_boletim = []
    for disciplina in aluno.turma.disciplinas:
        notas_disc = notas_por_disciplina.get(disciplina.id, [])
        
        # Agrupar por trimestre
        notas_por_trimestre = {}
        for nota in notas_disc:
            if nota.trimestre not in notas_por_trimestre:
                notas_por_trimestre[nota.trimestre] = []
            notas_por_trimestre[nota.trimestre].append(nota.valor)
        
        # Formatar notas
        lista_notas = []
        for trim in ["1º Trimestre", "2º Trimestre", "3º Trimestre"]:
            valores = notas_por_trimestre.get(trim, [])
            if valores:
                media = sum(valores) / len(valores)
                lista_notas.append({
                    "trimestre": trim,
                    "valor": round(media, 2),
                    "descricao": f"Média {trim}"
                })
            else:
                lista_notas.append({
                    "trimestre": trim,
                    "valor": None,
                    "descricao": "Sem nota"
                })
        
        # Calcular média
        valores_validos = [n["valor"] for n in lista_notas if n["valor"] is not None]
        media = round(sum(valores_validos) / len(valores_validos), 2) if valores_validos else 0
        
        linhas_boletim.append({
            "disciplina": disciplina.nome,
            "notas": lista_notas,
            "media_provisoria": media
        })
    
    return {
        "aluno_nome": aluno.nome,
        "aluno_bi": aluno.bi,
        "turma": aluno.turma.nome,
        "escola_id": aluno.escola_id,
        "escola_nome": aluno.escola.nome if aluno.escola else None,
        "linhas": linhas_boletim
    }
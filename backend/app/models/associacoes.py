# app/models/associacoes.py
""" Tabela de associação entre Turmas e Disciplinas (relação N:N)
    Cada turma pode ter várias disciplinas, e cada disciplina pode ser ensinada em várias turmas.
    Esta tabela é essencial para modelar a complexidade do currículo escolar, onde uma disciplina como "Matemática" pode ser parte do currículo de várias turmas, e uma turma como "10ª Classe A" pode ter várias disciplinas.
 """
from sqlalchemy import Table, Column, Integer, ForeignKey
from app.db.database import Base

# --- TABELA DE ASSOCIAÇÃO (N:N) ---
turma_disciplina = Table(
    'turma_disciplina',
    Base.metadata,
    Column('turma_id', Integer, ForeignKey('turmas.id', ondelete="CASCADE"), primary_key=True),
    Column('disciplina_id', Integer, ForeignKey('disciplinas.id', ondelete="CASCADE"), primary_key=True)
)
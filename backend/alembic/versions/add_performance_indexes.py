# backend/alembic/versions/add_performance_indexes.py - NOVA MIGRAÇÃO
"""Add performance indexes

Revision ID: perf_001
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # 1. Índices compostos para queries comuns
    
    # Alunos
    op.create_index(
        'idx_alunos_escola_turma',
        'alunos',
        ['escola_id', 'turma_id']
    )
    op.create_index(
        'idx_alunos_escola_ativo',
        'alunos',
        ['escola_id', 'ativo']
    )
    
    # Mensalidades (queries de relatórios financeiros)
    op.create_index(
        'idx_mensalidades_escola_estado',
        'mensalidades',
        ['escola_id', 'estado']
    )
    op.create_index(
        'idx_mensalidades_escola_vencimento',
        'mensalidades',
        ['escola_id', 'data_vencimento']
    )
    op.create_index(
        'idx_mensalidades_aluno_ano',
        'mensalidades',
        ['aluno_id', 'ano']
    )
    
    # Notas (queries de boletim)
    op.create_index(
        'idx_notas_aluno_disciplina',
        'notas',
        ['aluno_id', 'disciplina_id']
    )
    op.create_index(
        'idx_notas_disciplina_trimestre',
        'notas',
        ['disciplina_id', 'trimestre']
    )
    
    # Presenças
    op.create_index(
        'idx_presencas_turma_data',
        'presencas',
        ['turma_id', 'data']
    )
    op.create_index(
        'idx_presencas_aluno_presente',
        'presencas',
        ['aluno_id', 'presente']
    )
    
    # Usuários
    op.create_index(
        'idx_usuarios_escola_perfil',
        'usuarios',
        ['escola_id', 'perfil']
    )
    op.create_index(
        'idx_usuarios_email_ativo',
        'usuarios',
        ['email', 'ativo']
    )
    
    # Horários
    op.create_index(
        'idx_horarios_professor_dia',
        'horarios',
        ['professor_id', 'dia_semana']
    )
    op.create_index(
        'idx_horarios_turma_dia',
        'horarios',
        ['turma_id', 'dia_semana']
    )
    
    # 2. Índices parciais para casos específicos
    
    # Mensalidades pendentes (mais comuns)
    op.execute("""
        CREATE INDEX idx_mensalidades_pendentes 
        ON mensalidades (escola_id, aluno_id) 
        WHERE estado = 'Pendente'
    """)
    
    # Alunos ativos (maioria das queries)
    op.execute("""
        CREATE INDEX idx_alunos_ativos 
        ON alunos (escola_id, turma_id) 
        WHERE ativo = true
    """)
    
    # 3. Índices de texto para busca
    op.execute("""
        CREATE INDEX idx_alunos_nome_trgm 
        ON alunos USING gin (nome gin_trgm_ops)
    """)
    
    op.execute("""
        CREATE INDEX idx_usuarios_nome_trgm 
        ON usuarios USING gin (nome gin_trgm_ops)
    """)

def downgrade():
    # Remover índices
    op.drop_index('idx_alunos_escola_turma')
    op.drop_index('idx_alunos_escola_ativo')
    # ... etc
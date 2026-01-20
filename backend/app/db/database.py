# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. URL de Conexão com o Banco de Dados
# Formato: postgresql://usuario:senha@localhost/nome_do_banco
# ATENÇÃO: Substitui 'postgres' e 'password' pelas tuas credenciais reais do pgAdmin
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1qaz2wsX@localhost/erp_escolas_db"

# 2. Criar o Engine (o motor que fala com o banco)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Criar a Sessão Local
# Cada pedido (request) terá a sua própria sessão de banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Base para os Modelos
# Todas as nossas tabelas vão herdar desta classe 'Base'
Base = declarative_base()

# 5. Dependência para obter a BD (usaremos isto nas rotas do FastAPI)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
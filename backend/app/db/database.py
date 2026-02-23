# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Criação da engine com configurações de pool para melhor performance
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, # Verifica se a conexão está viva antes de usar
    pool_size=10,       # Mantém 10 conexões abertas
    max_overflow=20     # Permite criar mais 20 se necessário
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependência para injetar o DB nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
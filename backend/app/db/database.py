import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carrega as variáveis do ficheiro .env
load_dotenv()

# Lê a URL da variável de ambiente. Se não existir, lança erro.
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}")  # Para debug, remova ou comente esta linha em produção
if not DATABASE_URL:
    raise ValueError("A variável DATABASE_URL não está definida no ficheiro .env")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
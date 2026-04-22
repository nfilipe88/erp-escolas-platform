# Ficheiro: app/db/session.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback apenas para desenvolvimento local (não recomendado para produção)
    # Mas o ideal é garantir que está no .env
    print("AVISO: DATABASE_URL não encontrada no .env. A usar valor padrão.")
    DATABASE_URL = "postgresql+asyncpg://postgres:1qaz2wsX@localhost:5432/pigedb"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session
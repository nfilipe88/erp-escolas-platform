# backend/tests/conftest.py - CONFIGURAÇÃO DE TESTES
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.db.database import Base, get_db
from app.main import app
from app.models import usuario as models_user, aluno as models_aluno
from app.core.security import get_password_hash
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent))

# Database de teste em memória
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Criar banco de dados limpo para cada teste"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Cliente de teste com banco de dados"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def escola_fixture(db):
    """Criar escola de teste"""
    from app.models.escola import Escola
    
    escola = Escola(
        nome="Escola Teste",
        endereco="Rua Teste, 123",
        telefone="123456789",
        email="teste@escola.com"
    )
    db.add(escola)
    db.commit()
    db.refresh(escola)
    return escola

@pytest.fixture
def admin_user(db, escola_fixture):
    """Criar usuário admin de teste"""
    from app.models.usuario import Usuario
    from app.models.permission import Role
    
    # Criar role admin
    admin_role = Role(
        name="admin_escola",
        description="Admin de teste",
        is_system_role=True
    )
    db.add(admin_role)
    db.commit()
    
    # Criar usuário
    user = Usuario(
        nome="Admin Teste",
        email="admin@teste.com",
        senha_hash=get_password_hash("SenhaSegura123!"),
        role_id=admin_role.id,
        escola_id=escola_fixture.id,
        ativo=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, admin_user):
    """Headers com token de autenticação"""
    response = client.post(
        "/auth/login",
        data={
            "username": "admin@teste.com",
            "password": "SenhaSegura123!"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def aluno_fixture(db, escola_fixture):
    """Criar aluno de teste"""
    from app.models.aluno import Aluno
    from datetime import date
    
    aluno = Aluno(
        nome="João Silva",
        bi="123456789BA001",
        data_nascimento=date(2010, 5, 15),
        escola_id=escola_fixture.id,
        ativo=True
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)
    return aluno
# backend/tests/test_auth.py - TESTES DE AUTENTICAÇÃO
import pytest
from fastapi import status

class TestAuthentication:
    """Testes de autenticação"""
    
    def test_login_success(self, client, admin_user):
        """Teste de login bem-sucedido"""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin@teste.com",
                "password": "SenhaSegura123!"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client, admin_user):
        """Teste de login com credenciais inválidas"""
        response = client.post(
            "/auth/login",
            data={
                "username": "admin@teste.com",
                "password": "SenhaErrada"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Credenciais inválidas" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, db, admin_user):
        """Teste de login com usuário inativo"""
        # Desativar usuário
        admin_user.ativo = False
        db.commit()
        
        response = client.post(
            "/auth/login",
            data={
                "username": "admin@teste.com",
                "password": "SenhaSegura123!"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "desativada" in response.json()["detail"].lower()
    
    def test_register_user_success(self, client):
        """Teste de registro de novo usuário"""
        response = client.post(
            "/auth/registar",
            json={
                "nome": "Novo Usuário",
                "email": "novo@teste.com",
                "senha": "SenhaForte123!@#",
                "perfil": "professor"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "novo@teste.com"
        assert data["nome"] == "Novo Usuário"
    
    def test_register_weak_password(self, client):
        """Teste de registro com senha fraca"""
        response = client.post(
            "/auth/registar",
            json={
                "nome": "Usuário Teste",
                "email": "teste@teste.com",
                "senha": "123",  # Senha muito fraca
                "perfil": "professor"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "senha" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, admin_user):
        """Teste de registro com email duplicado"""
        response = client.post(
            "/auth/registar",
            json={
                "nome": "Outro Usuário",
                "email": "admin@teste.com",  # Email já existe
                "senha": "SenhaForte123!",
                "perfil": "professor"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já registado" in response.json()["detail"].lower()
    
    def test_refresh_token_success(self, client, admin_user):
        """Teste de refresh token"""
        # Fazer login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "admin@teste.com",
                "password": "SenhaSegura123!"
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Usar refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_token_invalid(self, client):
        """Teste de refresh token inválido"""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "token_invalido"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
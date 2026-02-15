# backend/tests/test_alunos.py - TESTES DE ALUNOS
import pytest
from fastapi import status
from datetime import date

class TestAlunos:
    """Testes do módulo de alunos"""
    
    def test_list_alunos_success(self, client, auth_headers, aluno_fixture):
        """Teste de listagem de alunos"""
        response = client.get("/alunos/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) >= 1
    
    def test_list_alunos_pagination(self, client, auth_headers, db, escola_fixture):
        """Teste de paginação de alunos"""
        from app.models.aluno import Aluno
        
        # Criar 25 alunos
        for i in range(25):
            aluno = Aluno(
                nome=f"Aluno {i}",
                escola_id=escola_fixture.id,
                ativo=True
            )
            db.add(aluno)
        db.commit()
        
        # Primeira página
        response = client.get("/alunos/?page=1&per_page=10", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] >= 25
        assert data["page"] == 1
        assert data["has_next"] is True
        
        # Segunda página
        response = client.get("/alunos/?page=2&per_page=10", headers=auth_headers)
        data = response.json()
        assert len(data["items"]) == 10
        assert data["page"] == 2
    
    def test_create_aluno_success(self, client, auth_headers, escola_fixture):
        """Teste de criação de aluno"""
        response = client.post(
            "/alunos/",
            headers=auth_headers,
            json={
                "nome": "Maria Santos",
                "bi": "987654321BA002",
                "data_nascimento": "2011-03-20",
                "escola_id": escola_fixture.id,
                "ativo": True
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == "Maria Santos"
        assert data["bi"] == "987654321BA002"
        assert data["ativo"] is True
    
    def test_create_aluno_invalid_bi(self, client, auth_headers, escola_fixture):
        """Teste de criação com BI inválido"""
        response = client.post(
            "/alunos/",
            headers=auth_headers,
            json={
                "nome": "Teste",
                "bi": "123",  # BI inválido
                "escola_id": escola_fixture.id
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "BI" in response.json()["detail"]
    
    def test_create_aluno_duplicate_bi(self, client, auth_headers, aluno_fixture):
        """Teste de criação com BI duplicado"""
        response = client.post(
            "/alunos/",
            headers=auth_headers,
            json={
                "nome": "Outro Aluno",
                "bi": aluno_fixture.bi,  # BI já existe
                "escola_id": aluno_fixture.escola_id
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "já existe" in response.json()["detail"].lower()
    
    def test_get_aluno_success(self, client, auth_headers, aluno_fixture):
        """Teste de busca de aluno por ID"""
        response = client.get(f"/alunos/{aluno_fixture.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == aluno_fixture.id
        assert data["nome"] == aluno_fixture.nome
    
    def test_get_aluno_not_found(self, client, auth_headers):
        """Teste de busca de aluno inexistente"""
        response = client.get("/alunos/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_aluno_success(self, client, auth_headers, aluno_fixture):
        """Teste de atualização de aluno"""
        response = client.put(
            f"/alunos/{aluno_fixture.id}",
            headers=auth_headers,
            json={"nome": "João Silva Atualizado"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nome"] == "João Silva Atualizado"
    
    def test_delete_aluno_success(self, client, auth_headers, aluno_fixture):
        """Teste de deleção de aluno"""
        response = client.delete(f"/alunos/{aluno_fixture.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se foi deletado
        get_response = client.get(f"/alunos/{aluno_fixture.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_search_alunos(self, client, auth_headers, aluno_fixture):
        """Teste de busca de alunos por nome"""
        response = client.get("/alunos/?search=João", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) >= 1
        assert "João" in data["items"][0]["nome"]
    
    def test_unauthorized_access(self, client, aluno_fixture):
        """Teste de acesso sem autenticação"""
        response = client.get("/alunos/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
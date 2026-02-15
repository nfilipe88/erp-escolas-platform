# backend/tests/test_audit.py - TESTES DE AUDITORIA
import pytest
from datetime import datetime, timedelta
from app.services.audit_service import AuditService

class TestAudit:
    """Testes do sistema de auditoria"""
    
    def test_log_action(self, db, admin_user, escola_fixture):
        """Teste de registro de ação"""
        service = AuditService(db)
        
        log = service.log_action(
            usuario_id=admin_user.id,
            usuario_email=admin_user.email,
            action="CREATE",
            entity_type="Aluno",
            entity_id=1,
            escola_id=escola_fixture.id,
            changes={"nome": "João Silva"},
            success=True
        )
        
        assert log.id is not None
        assert log.usuario_id == admin_user.id
        assert log.action == "CREATE"
        assert log.entity_type == "Aluno"
    
    def test_get_entity_history(self, db, admin_user, escola_fixture):
        """Teste de histórico de entidade"""
        service = AuditService(db)
        
        # Criar vários logs
        for i in range(5):
            service.log_action(
                usuario_id=admin_user.id,
                usuario_email=admin_user.email,
                action="UPDATE",
                entity_type="Aluno",
                entity_id=1,
                escola_id=escola_fixture.id,
                changes={"campo": f"valor{i}"}
            )
        
        # Buscar histórico
        history = service.get_entity_history("Aluno", 1)
        
        assert len(history) == 5
        assert all(log.entity_id == 1 for log in history)
    
    def test_detect_suspicious_activity_failed_logins(self, db, admin_user):
        """Teste de detecção de múltiplas falhas de login"""
        service = AuditService(db)
        
        # Simular 6 falhas de login
        for i in range(6):
            service.log_action(
                usuario_id=admin_user.id,
                usuario_email=admin_user.email,
                action="LOGIN",
                success=False
            )
        
        # Detectar atividade suspeita
        alerts = service.detect_suspicious_activity(admin_user.id)
        
        assert len(alerts) > 0
        assert any(alert["type"] == "MULTIPLE_FAILED_LOGINS" for alert in alerts)
        assert any(alert["severity"] == "HIGH" for alert in alerts)
# backend/app/services/audit_service.py - NOVO ARQUIVO
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json

class AuditService:
    """Serviço centralizado de auditoria"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        usuario_id: int,
        usuario_email: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        escola_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Registrar ação no log de auditoria"""
        
        log = AuditLog(
            usuario_id=usuario_id,
            usuario_email=usuario_email,
            escola_id=escola_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        
        return log
    
    def get_entity_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50
    ) -> list[AuditLog]:
        """Buscar histórico de uma entidade"""
        return self.db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type,
            AuditLog.entity_id == entity_id
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    def get_user_actions(
        self,
        usuario_id: int,
        days: int = 30,
        limit: int = 100
    ) -> list[AuditLog]:
        """Buscar ações de um usuário"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.db.query(AuditLog).filter(
            AuditLog.usuario_id == usuario_id,
            AuditLog.timestamp >= cutoff
        ).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    
    def get_escola_actions(
        self,
        escola_id: int,
        action_types: Optional[list[str]] = None,
        days: int = 7
    ) -> list[AuditLog]:
        """Buscar ações em uma escola"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(AuditLog).filter(
            AuditLog.escola_id == escola_id,
            AuditLog.timestamp >= cutoff
        )
        
        if action_types:
            query = query.filter(AuditLog.action.in_(action_types))
        
        return query.order_by(AuditLog.timestamp.desc()).all()
    
    def detect_suspicious_activity(self, usuario_id: int) -> list[Dict[str, Any]]:
        """Detectar atividades suspeitas"""
        alerts = []
        
        # 1. Muitas falhas de login
        failed_logins = self.db.query(AuditLog).filter(
            AuditLog.usuario_id == usuario_id,
            AuditLog.action == "LOGIN",
            AuditLog.success == False,
            AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).count()
        
        if failed_logins >= 5:
            alerts.append({
                "type": "MULTIPLE_FAILED_LOGINS",
                "severity": "HIGH",
                "count": failed_logins,
                "message": f"{failed_logins} tentativas de login falhadas na última hora"
            })
        
        # 2. Muitas exclusões em curto período
        recent_deletes = self.db.query(AuditLog).filter(
            AuditLog.usuario_id == usuario_id,
            AuditLog.action == "DELETE",
            AuditLog.timestamp >= datetime.utcnow() - timedelta(minutes=30)
        ).count()
        
        if recent_deletes >= 10:
            alerts.append({
                "type": "MASS_DELETION",
                "severity": "CRITICAL",
                "count": recent_deletes,
                "message": f"{recent_deletes} exclusões nos últimos 30 minutos"
            })
        
        # 3. Acesso fora do horário normal (00:00 - 06:00)
        hour = datetime.utcnow().hour
        if 0 <= hour < 6:
            recent_actions = self.db.query(AuditLog).filter(
                AuditLog.usuario_id == usuario_id,
                AuditLog.timestamp >= datetime.utcnow() - timedelta(hours=1)
            ).count()
            
            if recent_actions >= 5:
                alerts.append({
                    "type": "OFF_HOURS_ACTIVITY",
                    "severity": "MEDIUM",
                    "count": recent_actions,
                    "message": "Atividade suspeita fora do horário normal"
                })
        
        return alerts

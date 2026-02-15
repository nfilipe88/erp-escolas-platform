# backend/app/middleware/audit_middleware.py - NOVO ARQUIVO
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.services.audit_service import AuditService
from app.db.database import SessionLocal
import time
import json

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware para auditoria automática de requisições"""
    
    async def dispatch(self, request: Request, call_next):
        # Iniciar timer
        start_time = time.time()
        
        # Extrair info da requisição
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de resposta
        process_time = time.time() - start_time
        
        # Log apenas para operações de mudança (POST, PUT, DELETE)
        if method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Extrair usuário do request state (definido no auth)
            user = getattr(request.state, "user", None)
            
            if user:
                db = SessionLocal()
                try:
                    audit_service = AuditService(db)
                    
                    # Mapear path para action
                    action = self._extract_action(method, path)
                    entity_type, entity_id = self._extract_entity(path)
                    
                    audit_service.log_action(
                        usuario_id=user.id,
                        usuario_email=user.email,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        escola_id=user.escola_id,
                        metadata={
                            "ip": client_ip,
                            "method": method,
                            "path": path,
                            "status_code": response.status_code,
                            "response_time_ms": round(process_time * 1000, 2)
                        },
                        success=response.status_code < 400
                    )
                finally:
                    db.close()
        
        return response
    
    def _extract_action(self, method: str, path: str) -> str:
        """Extrair ação do método e path"""
        if method == "POST":
            return "CREATE"
        elif method == "PUT" or method == "PATCH":
            return "UPDATE"
        elif method == "DELETE":
            return "DELETE"
        return "UNKNOWN"
    
    def _extract_entity(self, path: str) -> tuple:
        """Extrair tipo e ID da entidade do path"""
        parts = path.strip("/").split("/")
        
        if len(parts) >= 1:
            entity_type = parts[0].rstrip("s")  # alunos -> aluno
            entity_id = None
            
            # Tentar extrair ID (normalmente segunda parte)
            if len(parts) >= 2 and parts[1].isdigit():
                entity_id = int(parts[1])
            
            return entity_type.upper(), entity_id
        
        return None, None
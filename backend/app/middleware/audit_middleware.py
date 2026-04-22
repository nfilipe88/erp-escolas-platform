# app/middleware/audit_middleware.py
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.concurrency import run_in_threadpool
from app.services.audit_service import AuditService
from app.db.database import SessionLocal

# Função isolada e síncrona para gravar na BD
def save_audit_log(user_id, user_email, escola_id, action, entity_type, entity_id, metadata, success):
    db = SessionLocal()
    try:
        audit_service = AuditService(db)
        audit_service.log_action(
            usuario_id=user_id,
            usuario_email=user_email,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            escola_id=escola_id,
            metadata=metadata,
            success=success
        )
    finally:
        db.close()

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware para auditoria automática de requisições"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Processar requisição imediatamente
        response = await call_next(request)
        
        # Calcular tempo de resposta
        process_time = time.time() - start_time
        
        # Log apenas para operações de mudança
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # O get_current_user agora injeta o utilizador aqui!
            user = getattr(request.state, "user", None)
            
            if user:
                action = self._extract_action(request.method, request.url.path)
                entity_type, entity_id = self._extract_entity(request.url.path)
                
                metadata = {
                    "ip": request.client.host if request.client else "unknown",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "response_time_ms": round(process_time * 1000, 2)
                }
                
                # Executa a gravação na BD de forma assíncrona (não bloqueia a resposta!)
                await run_in_threadpool(
                    save_audit_log,
                    user.id, user.email, user.escola_id, action, entity_type, entity_id, metadata, response.status_code < 400
                )
        
        return response
    
    def _extract_action(self, method: str, path: str) -> str:
        if method == "POST": return "CREATE"
        elif method in ["PUT", "PATCH"]: return "UPDATE"
        elif method == "DELETE": return "DELETE"
        return "UNKNOWN"
    
    def _extract_entity(self, path: str) -> tuple:
        parts = path.strip("/").split("/")
        if len(parts) >= 1:
            entity_type = parts[0].rstrip("s")
            entity_id = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else None
            return entity_type.upper(), entity_id
        return None, None
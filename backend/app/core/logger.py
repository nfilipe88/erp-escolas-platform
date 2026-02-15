# backend/app/core/logger.py - NOVO ARQUIVO
import asyncio
import logging
from functools import wraps
import time
from typing import Callable

# Loggers específicos
app_logger = logging.getLogger("app")
security_logger = logging.getLogger("security")
performance_logger = logging.getLogger("performance")

def log_execution_time(func: Callable):
    """Decorator para logar tempo de execução"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start
            
            performance_logger.info(
                f"Function executed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start
            performance_logger.error(
                f"Function failed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                    "success": False
                }
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            performance_logger.info(
                f"Function executed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True
                }
            )
            return result
        except Exception as e:
            duration = time.time() - start
            performance_logger.error(
                f"Function failed",
                extra={
                    "function": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                    "success": False
                }
            )
            raise
    
    # Retornar wrapper correto
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def log_security_event(event_type: str, details: dict):
    """Logar evento de segurança"""
    security_logger.warning(
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            **details
        }
    )
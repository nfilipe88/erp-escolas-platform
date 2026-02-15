# backend/app/core/cache.py - NOVO ARQUIVO
import asyncio
from redis import Redis
from typing import Optional, Any
import json
import pickle
from functools import wraps
from app.core.config import settings

class CacheService:
    """Serviço de cache com Redis"""
    
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=False,  # Para suportar pickle
            socket_connect_timeout=5
        )
        self.default_ttl = 300  # 5 minutos
    
    def get(self, key: str) -> Optional[Any]:
        """Buscar valor do cache"""
        try:
            value = self.redis.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Salvar no cache"""
        try:
            ttl = ttl or self.default_ttl
            serialized = pickle.dumps(value)
            return self.redis.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Deletar do cache"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Deletar todas as chaves que correspondem ao padrão"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error: {e}")
            return 0
    
    def clear_escola_cache(self, escola_id: int):
        """Limpar todo o cache de uma escola"""
        self.delete_pattern(f"escola:{escola_id}:*")

# Instância global
cache = CacheService()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator para cachear resultados de funções"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Gerar chave do cache
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Tentar buscar do cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Salvar no cache
            cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
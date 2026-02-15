# backend/app/services/dashboard_service.py - USANDO CACHE
from app.core.cache import cache, cached

class DashboardService:
    
    @cached(ttl=60, key_prefix="dashboard")  # Cache de 1 minuto
    def get_stats(self, escola_id: Optional[int] = None) -> dict:
        """Buscar estatísticas com cache"""
        
        # Queries pesadas...
        stats = crud_dashboard.get_stats(db, escola_id)
        
        return stats
    
    def invalidate_cache(self, escola_id: int):
        """Invalidar cache quando dados mudam"""
        cache.delete_pattern(f"dashboard:*escola_id={escola_id}*")
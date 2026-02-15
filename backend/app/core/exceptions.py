# backend/app/core/exceptions.py - NOVO ARQUIVO
class BusinessLogicError(Exception):
    """Exceção para erros de lógica de negócio"""
    pass

class PermissionDeniedError(Exception):
    """Exceção para erros de permissão"""
    pass

class ResourceNotFoundError(Exception):
    """Exceção para recursos não encontrados"""
    pass

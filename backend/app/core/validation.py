# backend/app/core/validation.py - NOVO ARQUIVO
from pydantic import validator, BaseModel
import bleach
import re

class InputSanitizer:
    """Sanitização centralizada de inputs"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Remover caracteres perigosos"""
        if not value:
            return value
        
        # Limitar tamanho
        value = value[:max_length]
        
        # Remover caracteres de controle
        value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Escapar HTML
        value = bleach.clean(value, strip=True)
        
        return value.strip()
    
    @staticmethod
    def sanitize_bi(bi: str) -> str:
        """Validar e limpar número de BI"""
        # Remover espaços e caracteres especiais
        bi = re.sub(r'[^A-Z0-9]', '', bi.upper())
        
        # Validar formato (ajustar conforme regras de Angola)
        if not re.match(r'^[0-9]{9}[A-Z]{2}[0-9]{3}$', bi):
            raise ValueError("Formato de BI inválido")
        
        return bi
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Validar e normalizar email"""
        email = email.lower().strip()
        
        # Validação básica
        if not re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', email):
            raise ValueError("Email inválido")
        
        return email
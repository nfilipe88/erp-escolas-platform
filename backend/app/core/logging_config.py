# backend/app/core/logging_config.py - NOVO ARQUIVO
import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import json
from datetime import datetime
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formatter JSON customizado"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Adicionar timestamp ISO
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Adicionar nível
        log_record['level'] = record.levelname
        
        # Adicionar contexto da aplicação
        log_record['app'] = 'erp-escolar'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

def setup_logging():
    """Configurar sistema de logging"""
    
    # Criar diretório de logs
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Logger raiz
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 1. Console Handler (desenvolvimento)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 2. File Handler - Geral (JSON para parse fácil)
    file_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    # 3. Error Handler - Apenas erros (rotação diária)
    error_handler = TimedRotatingFileHandler(
        log_dir / "errors.log",
        when="midnight",
        interval=1,
        backupCount=30
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    logger.addHandler(error_handler)
    
    # 4. Security Handler - Eventos de segurança
    security_handler = RotatingFileHandler(
        log_dir / "security.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(json_formatter)
    
    # Criar logger específico para segurança
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    
    # 5. Performance Handler - Métricas de performance
    perf_handler = RotatingFileHandler(
        log_dir / "performance.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(json_formatter)
    
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)
    
    # Suprimir logs muito verbosos em produção
    if os.getenv('ENVIRONMENT') == 'production':
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger

# Logger global
logger = setup_logging()
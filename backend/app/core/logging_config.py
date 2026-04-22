# app/core/logging_config.py
import logging
import os
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone

# Importação robusta para diferentes versões do python-json-logger
try:
    from pythonjsonlogger import jsonlogger
    # Verifica onde está o JsonFormatter (varia conforme versão)
    if hasattr(jsonlogger, 'JsonFormatter'):
        BaseJsonFormatter = jsonlogger.JsonFormatter # type: ignore
    else:
        from pythonjsonlogger.json import JsonFormatter as BaseJsonFormatter # type: ignore
except ImportError:
    # Fallback se não instalado
    BaseJsonFormatter = logging.Formatter

class CustomJsonFormatter(BaseJsonFormatter): # type: ignore
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.now(timezone.utc).isoformat()
        log_record['level'] = record.levelname
        log_record['app'] = 'erp-escolar'

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Se já tem handlers, não adiciona novos (evita duplicação no reload)
    if logger.handlers:
        return

    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    file_handler = RotatingFileHandler(
        log_dir / "app.log", maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
import json
import logging
import sys
from datetime import datetime
from typing import Any

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
        }
        
        # Capture extra fields passed to logger
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
            
        # Capture exceptions if they exist
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_entry)

def setup_logging():
    root_logger = logging.getLogger()
    
    # Avoid duplicate handlers if setup is called multiple times
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Suppress verbose standard loggers if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

# Structured logging wrapper
class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def info(self, msg: str, **kwargs):
        self.logger.info(msg, extra={"extra_fields": kwargs})
        
    def warning(self, msg: str, **kwargs):
        self.logger.warning(msg, extra={"extra_fields": kwargs})
        
    def error(self, msg: str, **kwargs):
        self.logger.error(msg, extra={"extra_fields": kwargs})
        
    def exception(self, msg: str, **kwargs):
        self.logger.exception(msg, extra={"extra_fields": kwargs})

logger = StructuredLogger("veritas_ai")

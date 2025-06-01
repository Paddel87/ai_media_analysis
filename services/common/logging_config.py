import logging
import sys
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime
import os
from typing import Optional, Dict, Any


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if hasattr(record, "extra"):
            log_record.update(record.extra)

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    # Erstelle Logs-Verzeichnis falls nicht vorhanden
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Konfiguriere Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Datei Handler mit Rotation
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, f"{service_name}.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Erstelle Service-spezifischen Logger
    logger = logging.getLogger(service_name)

    return logger


class ServiceLogger:
    def __init__(self, service_name: str, log_level: str = "INFO") -> None:
        self.logger = setup_logging(service_name, log_level)

    def log_error(
        self,
        message: str,
        error: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Loggt einen Fehler mit zusätzlichen Informationen"""
        log_data = extra or {}
        if error:
            log_data["error_type"] = type(error).__name__
            log_data["error_message"] = str(error)
        self.logger.error(message, extra=log_data, exc_info=bool(error))

    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Loggt eine Warnung mit zusätzlichen Informationen"""
        self.logger.warning(message, extra=extra or {})

    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Loggt eine Information mit zusätzlichen Details"""
        self.logger.info(message, extra=extra or {})

    def log_debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Loggt Debug-Informationen"""
        self.logger.debug(message, extra=extra or {})

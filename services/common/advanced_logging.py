import json
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class StructuredLogFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
            "thread_name": record.threadName,
        }

        # Extra-Felder hinzufügen
        if hasattr(record, "extra"):
            log_record.update(record.extra)

        # Exception-Informationen hinzufügen
        if record.exc_info:
            log_record["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "stack_trace": self.formatException(record.exc_info),
            }

        return json.dumps(log_record)


class AdvancedLogger:
    def __init__(
        self,
        service_name: str,
        log_dir: str = "logs",
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Initialisiert den Advanced Logger

        Args:
            service_name: Name des Services
            log_dir: Verzeichnis für Log-Dateien
            log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximale Größe einer Log-Datei
            backup_count: Anzahl der Backup-Dateien
        """
        self.service_name = service_name
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())

        # Log-Verzeichnis erstellen
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Logger konfigurieren
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(self.log_level)

        # Bestehende Handler entfernen
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # File Handler mit Rotation
        log_file = self.log_dir / f"{service_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(StructuredLogFormatter())
        self.logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(StructuredLogFormatter())
        self.logger.addHandler(console_handler)

    def log(
        self,
        level: str,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        """
        Loggt eine Nachricht mit zusätzlichen Informationen

        Args:
            level: Log-Level
            message: Log-Nachricht
            extra: Zusätzliche Informationen
            exc_info: Exception-Informationen
        """
        log_data = extra or {}
        log_data["service"] = self.service_name

        if exc_info:
            self.logger.exception(message, extra=log_data, exc_info=exc_info)
        else:
            log_method = getattr(self.logger, level.lower())
            log_method(message, extra=log_data)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log("DEBUG", message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log("INFO", message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log("WARNING", message, extra)

    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        self.log("ERROR", message, extra, exc_info)

    def critical(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        self.log("CRITICAL", message, extra, exc_info)

    def get_log_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über die Log-Dateien zurück
        """
        stats = {
            "service": self.service_name,
            "log_dir": str(self.log_dir),
            "current_log_file": str(self.log_dir / f"{self.service_name}.log"),
            "backup_files": [],
            "total_size": 0,
        }

        # Backup-Dateien auflisten
        for log_file in self.log_dir.glob(f"{self.service_name}.*.log"):
            file_stats = log_file.stat()
            stats["backup_files"].append(
                {
                    "name": log_file.name,
                    "size": file_stats.st_size,
                    "modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                }
            )
            stats["total_size"] += file_stats.st_size

        return stats

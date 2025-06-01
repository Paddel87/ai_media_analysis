import logging
from typing import Dict, Any, Optional, Type, List
from datetime import datetime
import traceback
import json
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    VALIDATION = "validation"
    NETWORK = "network"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    CLOUD = "cloud"
    UI = "ui"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorContext:
    def __init__(
        self,
        service: str,
        operation: str,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None,
    ):
        self.service = service
        self.operation = operation
        self.user_id = user_id
        self.request_id = request_id
        self.additional_info = additional_info or {}
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service": self.service,
            "operation": self.operation,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "additional_info": self.additional_info,
            "timestamp": self.timestamp.isoformat(),
        }


class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger("error_handler")
        self._error_handlers: Dict[Type[Exception], List[callable]] = {}
        self._error_categories: Dict[Type[Exception], ErrorCategory] = {}
        self._error_severities: Dict[Type[Exception], ErrorSeverity] = {}

    def register_error_handler(
        self,
        exception_type: Type[Exception],
        handler: callable,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ):
        """
        Registriert einen Error-Handler für einen bestimmten Exception-Typ
        """
        if exception_type not in self._error_handlers:
            self._error_handlers[exception_type] = []
        self._error_handlers[exception_type].append(handler)
        self._error_categories[exception_type] = category
        self._error_severities[exception_type] = severity

    def handle_error(self, error: Exception, context: ErrorContext) -> None:
        """
        Behandelt einen Fehler basierend auf seinem Typ und Kontext
        """
        error_type = type(error)
        error_info = {
            "error_type": error_type.__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": context.to_dict(),
            "category": self._error_categories.get(
                error_type, ErrorCategory.UNKNOWN
            ).value,
            "severity": self._error_severities.get(
                error_type, ErrorSeverity.MEDIUM
            ).value,
        }

        # Logging
        self.logger.error(
            f"Error occurred: {error_info['error_type']} - {error_info['error_message']}",
            extra=error_info,
        )

        # Error-Handler aufrufen
        handlers = self._error_handlers.get(error_type, [])
        for handler in handlers:
            try:
                handler(error, context)
            except Exception as handler_error:
                self.logger.error(
                    f"Error in error handler: {str(handler_error)}", exc_info=True
                )

    def get_error_stats(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über aufgetretene Fehler zurück
        """
        return {
            "registered_handlers": len(self._error_handlers),
            "error_categories": {
                category.value: len(
                    [e for e, c in self._error_categories.items() if c == category]
                )
                for category in ErrorCategory
            },
            "error_severities": {
                severity.value: len(
                    [e for e, s in self._error_severities.items() if s == severity]
                )
                for severity in ErrorSeverity
            },
        }

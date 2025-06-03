"""
Basis-Klasse für alle Services im AI Media Analysis System.

Diese Klasse implementiert die Standards aus .cursorrules für einheitliche
Service-Architektur, Health-Checks und Logging.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, Optional

import redis
from fastapi import FastAPI


class ServiceBase(ABC):
    """
    Basis für alle Services im AI Media Analysis System.

    Implementiert die .cursorrules Standards für:
    - Einheitliche Health-Checks
    - Standardisierte Error-Handling
    - Async-First Patterns
    - Logging-Integration
    """

    def __init__(
        self,
        service_name: str,
        redis_client: Optional[redis.Redis] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialisiert den Base Service.

        Args:
            service_name: Name des Services
            redis_client: Optionale Redis-Verbindung
            logger: Optionaler Logger
        """
        self.service_name = service_name
        self.redis_client = redis_client
        self.logger = logger or logging.getLogger(service_name)
        self.start_time = time.time()
        self._health_checks: Dict[str, Callable[[], Awaitable[Dict[str, Any]]]] = {}

    async def health_check(self) -> Dict[str, Any]:
        """
        Standard Health-Check-Endpoint.

        Returns:
            Dict mit Service-Status und Metriken
        """
        health_data = {
            "status": "healthy",
            "service": self.service_name,
            "timestamp": datetime.now().isoformat(),
            "uptime": time.time() - self.start_time,
        }

        # Redis-Status prüfen
        if self.redis_client:
            try:
                # Redis ping ausführen (kann sync oder async sein)
                self.redis_client.ping()  # type: ignore
                health_data["redis_connected"] = True
            except Exception:
                health_data["redis_connected"] = False
                health_data["status"] = "degraded"

        # Service-spezifische Health-Checks
        try:
            service_health = await self._service_health_check()
            health_data.update(service_health)
        except Exception as e:
            self.logger.error(f"Service health check failed: {e}")
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)

        return health_data

    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptverarbeitungs-Methode des Services.

        Args:
            data: Input-Daten für Verarbeitung

        Returns:
            Verarbeitungsergebnis
        """
        pass

    async def _service_health_check(self) -> Dict[str, Any]:
        """
        Service-spezifische Health-Checks.

        Kann von abgeleiteten Klassen überschrieben werden.

        Returns:
            Dict mit service-spezifischen Metriken
        """
        return {}

    def register_health_check(
        self, name: str, check_func: Callable[[], Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        Registriert einen benutzerdefinierten Health-Check.

        Args:
            name: Name des Checks
            check_func: Async-Funktion für den Check
        """
        self._health_checks[name] = check_func

    async def start(self) -> None:
        """
        Startet den Service.

        Implementiert Service-Startup-Logik.
        """
        self.logger.info(f"Starting service: {self.service_name}")

    async def stop(self) -> None:
        """
        Stoppt den Service graceful.

        Implementiert Service-Shutdown-Logik.
        """
        self.logger.info(f"Stopping service: {self.service_name}")

    def create_fastapi_app(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: str = "1.0.0",
    ) -> FastAPI:
        """
        Erstellt eine standardisierte FastAPI-App.

        Args:
            title: App-Titel
            description: App-Beschreibung
            version: App-Version

        Returns:
            Konfigurierte FastAPI-Instanz
        """
        app = FastAPI(
            title=title or f"{self.service_name} API",
            description=description or f"API für {self.service_name}",
            version=version,
        )

        # Standard Health-Check-Endpoint hinzufügen
        @app.get("/health")  # noqa: F811
        async def health_endpoint() -> Dict[str, Any]:
            return await self.health_check()

        return app

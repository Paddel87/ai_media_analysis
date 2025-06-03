import logging
from datetime import datetime
from typing import Dict, List, Optional

import requests

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service_integration")


class ServiceIntegration:
    def __init__(self, config: Dict):
        """
        Initialisiert die Service-Integration

        Args:
            config: Konfiguration mit Service-URLs
        """
        self.config = config
        self.services = {}
        self._init_services()

    def _init_services(self):
        """
        Initialisiert die Service-Verbindungen
        """
        # Vector DB Service
        if "vector_db_url" in self.config:
            from .vector_integration import VectorDBIntegration

            self.services["vector_db"] = VectorDBIntegration(
                vector_db_url=self.config["vector_db_url"]
            )

        # Media Service
        if "media_service_url" in self.config:
            from .media_integration import MediaServiceIntegration

            self.services["media"] = MediaServiceIntegration(
                media_service_url=self.config["media_service_url"]
            )

        # Analytics Service
        if "analytics_service_url" in self.config:
            self.services["analytics"] = AnalyticsServiceIntegration(
                analytics_service_url=self.config["analytics_service_url"]
            )

        # Cache Service
        if "cache_service_url" in self.config:
            self.services["cache"] = CacheServiceIntegration(
                cache_service_url=self.config["cache_service_url"]
            )

        # Monitoring Service
        if "monitoring_service_url" in self.config:
            self.services["monitoring"] = MonitoringServiceIntegration(
                monitoring_service_url=self.config["monitoring_service_url"]
            )

    def get_service(self, service_name: str):
        """
        Gibt einen Service zurück

        Args:
            service_name: Name des Services

        Returns:
            Service-Instanz oder None
        """
        return self.services.get(service_name)

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status aller Services

        Returns:
            Dictionary mit Health-Status pro Service
        """
        health = {}

        for name, service in self.services.items():
            try:
                health[name] = service.get_health()
            except Exception as e:
                health[name] = {"status": "unhealthy", "error": str(e)}

        return health


class AnalyticsServiceIntegration:
    def __init__(self, analytics_service_url: str = "http://analytics-service:8000"):
        self.analytics_service_url = analytics_service_url

    def track_embedding_usage(
        self, embedding_id: str, usage_type: str, metadata: Dict
    ) -> bool:
        """
        Verfolgt die Nutzung von Embeddings
        """
        try:
            response = requests.post(
                f"{self.analytics_service_url}/track/embedding",
                json={
                    "embedding_id": embedding_id,
                    "usage_type": usage_type,
                    "metadata": metadata,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Tracking: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Tracking: {str(e)}")
            raise

    def get_embedding_stats(self, embedding_id: str) -> Dict:
        """
        Gibt Statistiken für ein Embedding zurück
        """
        try:
            response = requests.get(
                f"{self.analytics_service_url}/stats/embedding/{embedding_id}"
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Abrufen der Statistiken: {response.text}")
                return {}

            return response.json()

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Statistiken: {str(e)}")
            raise

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status des Analytics Services
        """
        try:
            response = requests.get(f"{self.analytics_service_url}/health")

            if response.status_code != 200:
                return {"status": "unhealthy", "error": response.text}

            return response.json()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class CacheServiceIntegration:
    def __init__(self, cache_service_url: str = "http://cache-service:8000"):
        self.cache_service_url = cache_service_url

    def get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """
        Holt ein Embedding aus dem Cache
        """
        try:
            response = requests.get(f"{self.cache_service_url}/embedding/{text}")

            if response.status_code == 404:
                return None

            if response.status_code != 200:
                logger.error(f"Fehler beim Abrufen aus dem Cache: {response.text}")
                return None

            return response.json()["embedding"]

        except Exception as e:
            logger.error(f"Fehler beim Abrufen aus dem Cache: {str(e)}")
            raise

    def cache_embedding(
        self, text: str, embedding: List[float], ttl: int = 3600
    ) -> bool:
        """
        Speichert ein Embedding im Cache
        """
        try:
            response = requests.post(
                f"{self.cache_service_url}/embedding",
                json={"text": text, "embedding": embedding, "ttl": ttl},
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Speichern im Cache: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Speichern im Cache: {str(e)}")
            raise

    def invalidate_embedding(self, text: str) -> bool:
        """
        Entfernt ein Embedding aus dem Cache
        """
        try:
            response = requests.delete(f"{self.cache_service_url}/embedding/{text}")

            if response.status_code != 200:
                logger.error(f"Fehler beim Entfernen aus dem Cache: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Entfernen aus dem Cache: {str(e)}")
            raise

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status des Cache Services
        """
        try:
            response = requests.get(f"{self.cache_service_url}/health")

            if response.status_code != 200:
                return {"status": "unhealthy", "error": response.text}

            return response.json()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class MonitoringServiceIntegration:
    def __init__(self, monitoring_service_url: str = "http://monitoring-service:8000"):
        self.monitoring_service_url = monitoring_service_url

    def track_request(
        self, service: str, endpoint: str, duration: float, status: int
    ) -> bool:
        """
        Verfolgt API-Anfragen
        """
        try:
            response = requests.post(
                f"{self.monitoring_service_url}/track/request",
                json={
                    "service": service,
                    "endpoint": endpoint,
                    "duration": duration,
                    "status": status,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Tracking: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Tracking: {str(e)}")
            raise

    def track_error(self, service: str, error: str, context: Dict) -> bool:
        """
        Verfolgt Fehler
        """
        try:
            response = requests.post(
                f"{self.monitoring_service_url}/track/error",
                json={
                    "service": service,
                    "error": error,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Tracking: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Tracking: {str(e)}")
            raise

    def get_service_metrics(self, service: str) -> Dict:
        """
        Gibt Metriken für einen Service zurück
        """
        try:
            response = requests.get(f"{self.monitoring_service_url}/metrics/{service}")

            if response.status_code != 200:
                logger.error(f"Fehler beim Abrufen der Metriken: {response.text}")
                return {}

            return response.json()

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Metriken: {str(e)}")
            raise

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status des Monitoring Services
        """
        try:
            response = requests.get(f"{self.monitoring_service_url}/health")

            if response.status_code != 200:
                return {"status": "unhealthy", "error": response.text}

            return response.json()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

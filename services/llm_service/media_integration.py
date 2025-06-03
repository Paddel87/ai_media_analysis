import logging
from typing import Dict, List

import requests

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_media_integration")


class MediaServiceIntegration:
    def __init__(self, media_service_url: str = "http://media-service:8000"):
        self.media_service_url = media_service_url

    def analyze_media(self, media_id: str, analysis_type: str = "full") -> Dict:
        """
        Analysiert ein Medium mit dem LLM Service
        """
        try:
            # Medium abrufen
            media_response = requests.get(f"{self.media_service_url}/media/{media_id}")

            if media_response.status_code != 200:
                logger.error(f"Fehler beim Abrufen des Mediums: {media_response.text}")
                return None

            media_data = media_response.json()

            # Analyse durchführen
            analysis_request = {
                "media_id": media_id,
                "type": analysis_type,
                "metadata": media_data.get("metadata", {}),
                "content": media_data.get("content", ""),
            }

            analysis_response = requests.post(
                f"{self.media_service_url}/analyze", json=analysis_request
            )

            if analysis_response.status_code != 200:
                logger.error(f"Fehler bei der Analyse: {analysis_response.text}")
                return None

            return analysis_response.json()

        except Exception as e:
            logger.error(f"Fehler bei der Medienanalyse: {str(e)}")
            raise

    def generate_media_description(self, media_id: str, style: str = "neutral") -> str:
        """
        Generiert eine Beschreibung für ein Medium
        """
        try:
            # Medium abrufen
            media_response = requests.get(f"{self.media_service_url}/media/{media_id}")

            if media_response.status_code != 200:
                logger.error(f"Fehler beim Abrufen des Mediums: {media_response.text}")
                return None

            media_data = media_response.json()

            # Beschreibung generieren
            description_request = {
                "media_id": media_id,
                "style": style,
                "metadata": media_data.get("metadata", {}),
                "content": media_data.get("content", ""),
            }

            description_response = requests.post(
                f"{self.media_service_url}/describe", json=description_request
            )

            if description_response.status_code != 200:
                logger.error(
                    f"Fehler bei der Beschreibungsgenerierung: {description_response.text}"
                )
                return None

            return description_response.json().get("description")

        except Exception as e:
            logger.error(f"Fehler bei der Beschreibungsgenerierung: {str(e)}")
            raise

    def search_similar_media(self, media_id: str, limit: int = 5) -> List[Dict]:
        """
        Sucht ähnliche Medien
        """
        try:
            # Medium abrufen
            media_response = requests.get(f"{self.media_service_url}/media/{media_id}")

            if media_response.status_code != 200:
                logger.error(f"Fehler beim Abrufen des Mediums: {media_response.text}")
                return []

            media_data = media_response.json()

            # Ähnliche Medien suchen
            search_request = {
                "media_id": media_id,
                "limit": limit,
                "metadata": media_data.get("metadata", {}),
            }

            search_response = requests.post(
                f"{self.media_service_url}/search-similar", json=search_request
            )

            if search_response.status_code != 200:
                logger.error(f"Fehler bei der Mediensuche: {search_response.text}")
                return []

            return search_response.json().get("results", [])

        except Exception as e:
            logger.error(f"Fehler bei der Mediensuche: {str(e)}")
            raise

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status des Media Services
        """
        try:
            response = requests.get(f"{self.media_service_url}/health")

            if response.status_code != 200:
                return {"status": "unhealthy", "error": response.text}

            return response.json()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

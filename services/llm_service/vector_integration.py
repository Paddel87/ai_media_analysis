import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import requests

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_vector_integration")


class VectorDBIntegration:
    def __init__(self, vector_db_url: str = "http://vector-db:8000"):
        self.vector_db_url = vector_db_url
        self.collection_name = "llm_embeddings"
        self.vector_size = 1536  # Größe der OpenAI Embeddings

    def _create_collection_if_not_exists(self):
        """
        Erstellt die Collection, falls sie nicht existiert
        """
        try:
            # Collection-Konfiguration
            config = {
                "name": self.collection_name,
                "vector_size": self.vector_size,
                "distance": "Cosine",
            }

            # Collection erstellen
            response = requests.post(f"{self.vector_db_url}/collections", json=config)

            if response.status_code not in [200, 201]:
                logger.error(f"Fehler beim Erstellen der Collection: {response.text}")

        except Exception as e:
            logger.error(f"Fehler bei der Collection-Erstellung: {str(e)}")
            raise

    def store_embedding(
        self, text: str, embedding: List[float], metadata: Dict
    ) -> bool:
        """
        Speichert ein Embedding in der Vector DB
        """
        try:
            # Collection erstellen, falls nicht vorhanden
            self._create_collection_if_not_exists()

            # Vektor-ID generieren
            vector_id = str(uuid.uuid4())

            # Metadaten erweitern
            full_metadata = {
                **metadata,
                "text": text,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Vektor speichern
            vector_data = {
                "id": vector_id,
                "vector": embedding,
                "metadata": full_metadata,
                "collection": self.collection_name,
            }

            response = requests.post(f"{self.vector_db_url}/vectors", json=vector_data)

            if response.status_code != 200:
                logger.error(f"Fehler beim Speichern des Vektors: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Speichern des Embeddings: {str(e)}")
            raise

    def search_similar(
        self, embedding: List[float], limit: int = 5, score_threshold: float = 0.7
    ) -> List[Dict]:
        """
        Sucht ähnliche Embeddings
        """
        try:
            # Suchanfrage
            search_request = {
                "vector": embedding,
                "collection": self.collection_name,
                "limit": limit,
                "score_threshold": score_threshold,
            }

            response = requests.post(
                f"{self.vector_db_url}/search", json=search_request
            )

            if response.status_code != 200:
                logger.error(f"Fehler bei der Vektorsuche: {response.text}")
                return []

            results = response.json().get("results", [])
            return results

        except Exception as e:
            logger.error(f"Fehler bei der Ähnlichkeitssuche: {str(e)}")
            raise

    def delete_embedding(self, vector_id: str) -> bool:
        """
        Löscht ein Embedding
        """
        try:
            response = requests.delete(
                f"{self.vector_db_url}/vectors/{self.collection_name}/{vector_id}"
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Löschen des Vektors: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Löschen des Embeddings: {str(e)}")
            raise

    def get_health(self) -> Dict:
        """
        Prüft den Health-Status der Vector DB
        """
        try:
            response = requests.get(f"{self.vector_db_url}/health")

            if response.status_code != 200:
                return {"status": "unhealthy", "error": response.text}

            return response.json()

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def batch_store_embeddings(
        self, texts: List[str], embeddings: List[List[float]], metadata_list: List[Dict]
    ) -> List[bool]:
        """
        Speichert mehrere Embeddings in der Vector DB
        """
        try:
            # Collection erstellen, falls nicht vorhanden
            self._create_collection_if_not_exists()

            # Batch-Request vorbereiten
            batch_data = []

            for text, embedding, metadata in zip(texts, embeddings, metadata_list):
                vector_id = str(uuid.uuid4())

                full_metadata = {
                    **metadata,
                    "text": text,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                batch_data.append(
                    {
                        "id": vector_id,
                        "vector": embedding,
                        "metadata": full_metadata,
                        "collection": self.collection_name,
                    }
                )

            # Batch speichern
            response = requests.post(
                f"{self.vector_db_url}/vectors/batch", json={"vectors": batch_data}
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Batch-Speichern: {response.text}")
                return [False] * len(texts)

            return [True] * len(texts)

        except Exception as e:
            logger.error(f"Fehler beim Batch-Speichern: {str(e)}")
            raise

    def search_by_metadata(self, metadata_filter: Dict, limit: int = 5) -> List[Dict]:
        """
        Sucht Embeddings nach Metadaten
        """
        try:
            # Suchanfrage
            search_request = {
                "collection": self.collection_name,
                "metadata_filter": metadata_filter,
                "limit": limit,
            }

            response = requests.post(
                f"{self.vector_db_url}/search/metadata", json=search_request
            )

            if response.status_code != 200:
                logger.error(f"Fehler bei der Metadaten-Suche: {response.text}")
                return []

            return response.json().get("results", [])

        except Exception as e:
            logger.error(f"Fehler bei der Metadaten-Suche: {str(e)}")
            raise

    def update_metadata(self, vector_id: str, new_metadata: Dict) -> bool:
        """
        Aktualisiert die Metadaten eines Embeddings
        """
        try:
            response = requests.patch(
                f"{self.vector_db_url}/vectors/{self.collection_name}/{vector_id}/metadata",
                json=new_metadata,
            )

            if response.status_code != 200:
                logger.error(
                    f"Fehler beim Aktualisieren der Metadaten: {response.text}"
                )
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Metadaten: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict:
        """
        Gibt Statistiken über die Collection zurück
        """
        try:
            response = requests.get(
                f"{self.vector_db_url}/collections/{self.collection_name}/stats"
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Abrufen der Statistiken: {response.text}")
                return {}

            return response.json()

        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Statistiken: {str(e)}")
            raise

    def create_index(self, index_type: str = "HNSW") -> bool:
        """
        Erstellt einen Index für die Collection
        """
        try:
            response = requests.post(
                f"{self.vector_db_url}/collections/{self.collection_name}/index",
                json={"type": index_type},
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Erstellen des Index: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Index: {str(e)}")
            raise

    def delete_collection(self) -> bool:
        """
        Löscht die Collection
        """
        try:
            response = requests.delete(
                f"{self.vector_db_url}/collections/{self.collection_name}"
            )

            if response.status_code != 200:
                logger.error(f"Fehler beim Löschen der Collection: {response.text}")
                return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Löschen der Collection: {str(e)}")
            raise

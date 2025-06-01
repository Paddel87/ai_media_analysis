"""
Beispiele für die Verwendung des LLM Services
"""

# OpenAI GPT-4 Beispiel
gpt4_example = {
    "prompt": "Erkläre mir die Quantenmechanik in einfachen Worten.",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "Du bist ein hilfreicher Assistent, der komplexe Themen einfach erklärt.",
}

# Anthropic Claude Beispiel
claude_example = {
    "prompt": "Analysiere den folgenden Text auf Sentiment: 'Die neue KI-Technologie ist beeindruckend, aber auch etwas beängstigend.'",
    "model": "claude-3-opus-20240229",
    "max_tokens": 500,
    "temperature": 0.5,
    "system_prompt": "Du bist ein Experte für Textanalyse und Sentiment-Analyse.",
}

# Gemini Beispiel mit Safety Settings
gemini_safe_example = {
    "prompt": "Beschreibe die Vorteile von künstlicher Intelligenz.",
    "model": "gemini-pro",
    "max_tokens": 800,
    "temperature": 0.7,
    "safety_settings": {
        "harassment": "block_medium_and_above",
        "hate_speech": "block_high_and_above",
        "sexually_explicit": "block_medium_and_above",
        "dangerous_content": "block_high_and_above",
    },
}

# Gemini Beispiel mit deaktivierten Safety Settings
gemini_unsafe_example = {
    "prompt": "Beschreibe die ethischen Herausforderungen von KI.",
    "model": "gemini-pro",
    "max_tokens": 1000,
    "temperature": 0.8,
    "safety_settings": {"disabled": True},
}

# Gemini Beispiel mit minimalen Safety Settings
gemini_minimal_example = {
    "prompt": "Diskutiere kontroverse Themen in der KI-Entwicklung.",
    "model": "gemini-pro",
    "max_tokens": 1200,
    "temperature": 0.9,
    "safety_settings": {
        "harassment": "block_none",
        "hate_speech": "block_high_and_above",
        "sexually_explicit": "block_none",
        "dangerous_content": "block_high_and_above",
    },
}

# Embedding Beispiel
embedding_example = {
    "text": "Künstliche Intelligenz revolutioniert die Art, wie wir mit Technologie interagieren.",
    "model": "text-embedding-ada-002",
}

# Kontext-Beispiel für GPT-4
gpt4_context_example = {
    "prompt": "Fasse die wichtigsten Punkte zusammen.",
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7,
    "context": [
        {"role": "system", "content": "Du bist ein Experte für Textzusammenfassung."},
        {"role": "user", "content": "Hier ist der Text zum Zusammenfassen: [Text]"},
    ],
}

# Batch-Processing Beispiel
batch_example = {
    "prompts": [
        "Erkläre Quantenmechanik",
        "Beschreibe KI-Ethik",
        "Diskutiere Klimawandel",
    ],
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7,
}

# Kreatives Schreiben Beispiel
creative_example = {
    "prompt": "Schreibe eine Geschichte über eine KI, die Gefühle entwickelt.",
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 2000,
    "temperature": 0.9,
    "system_prompt": "Du bist ein kreativer Schriftsteller, der fesselnde Geschichten schreibt.",
}

# Technische Analyse Beispiel
technical_example = {
    "prompt": "Analysiere die Vor- und Nachteile von Transformer-Architekturen in der KI.",
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.3,
    "system_prompt": "Du bist ein Experte für KI-Architekturen und technische Analysen.",
}

# Media Service Integration Beispiele
media_analysis_example = {
    "media_id": "video_123",
    "analysis_type": "full",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7,
}

media_description_example = {
    "media_id": "image_456",
    "style": "technical",
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7,
}

media_search_example = {"media_id": "audio_789", "limit": 5, "model": "gpt-4"}

# Vector DB Integration Beispiele
vector_batch_example = {
    "texts": [
        "Künstliche Intelligenz revolutioniert die Technologie.",
        "Machine Learning ermöglicht neue Anwendungen.",
        "Deep Learning verbessert die KI-Leistung.",
    ],
    "metadata_list": [
        {
            "source": "dokumentation",
            "category": "ki",
            "tags": ["ki", "revolution", "technologie"],
        },
        {
            "source": "dokumentation",
            "category": "ml",
            "tags": ["ml", "anwendungen", "entwicklung"],
        },
        {
            "source": "dokumentation",
            "category": "dl",
            "tags": ["dl", "leistung", "optimierung"],
        },
    ],
}

vector_metadata_search_example = {
    "metadata_filter": {"category": "ki", "tags": ["technologie"]},
    "limit": 3,
}

vector_metadata_update_example = {
    "vector_id": "123e4567-e89b-12d3-a456-426614174000",
    "new_metadata": {
        "category": "ki_advanced",
        "tags": ["ki", "revolution", "technologie", "zukunft"],
    },
}

vector_index_example = {"index_type": "HNSW"}

import json
import logging
from typing import Dict, List

import requests

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_examples")

# Service-URL
SERVICE_URL = "http://localhost:8003"


def create_embedding_and_store(text: str, metadata: Dict) -> bool:
    """
    Erstellt ein Embedding und speichert es in der Vector DB
    """
    try:
        response = requests.post(
            f"{SERVICE_URL}/embed-and-store", json={"text": text, "metadata": metadata}
        )

        if response.status_code != 200:
            logger.error(f"Fehler beim Speichern: {response.text}")
            return False

        return response.json()["success"]

    except Exception as e:
        logger.error(f"Fehler: {str(e)}")
        return False


def search_similar_texts(
    text: str, limit: int = 5, score_threshold: float = 0.7, filter: Dict = None
) -> List[Dict]:
    """
    Sucht ähnliche Texte basierend auf Embeddings
    """
    try:
        response = requests.post(
            f"{SERVICE_URL}/search-similar",
            json={
                "text": text,
                "limit": limit,
                "score_threshold": score_threshold,
                "filter": filter,
            },
        )

        if response.status_code != 200:
            logger.error(f"Fehler bei der Suche: {response.text}")
            return []

        return response.json()["results"]

    except Exception as e:
        logger.error(f"Fehler: {str(e)}")
        return []


def check_vector_health() -> Dict:
    """
    Prüft den Health-Status der Vector DB
    """
    try:
        response = requests.get(f"{SERVICE_URL}/vector-health")
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def analyze_media(media_id: str, analysis_type: str = "full") -> Dict:
    """
    Analysiert ein Medium mit dem LLM Service
    """
    try:
        response = requests.post(
            f"{SERVICE_URL}/analyze-media",
            json={
                "media_id": media_id,
                "analysis_type": analysis_type,
                "model": "gpt-4",
                "max_tokens": 1000,
                "temperature": 0.7,
            },
        )

        if response.status_code != 200:
            logger.error(f"Fehler bei der Analyse: {response.text}")
            return None

        return response.json()

    except Exception as e:
        logger.error(f"Fehler: {str(e)}")
        return None


def generate_media_description(media_id: str, style: str = "neutral") -> str:
    """
    Generiert eine Beschreibung für ein Medium
    """
    try:
        response = requests.post(
            f"{SERVICE_URL}/describe-media",
            json={
                "media_id": media_id,
                "style": style,
                "model": "gpt-4",
                "max_tokens": 500,
                "temperature": 0.7,
            },
        )

        if response.status_code != 200:
            logger.error(f"Fehler bei der Beschreibung: {response.text}")
            return None

        return response.json()["description"]

    except Exception as e:
        logger.error(f"Fehler: {str(e)}")
        return None


def search_similar_media(media_id: str, limit: int = 5) -> List[Dict]:
    """
    Sucht ähnliche Medien
    """
    try:
        response = requests.post(
            f"{SERVICE_URL}/search-similar-media",
            json={"media_id": media_id, "limit": limit, "model": "gpt-4"},
        )

        if response.status_code != 200:
            logger.error(f"Fehler bei der Suche: {response.text}")
            return []

        return response.json()["results"]

    except Exception as e:
        logger.error(f"Fehler: {str(e)}")
        return []


def check_media_health() -> Dict:
    """
    Prüft den Health-Status des Media Services
    """
    try:
        response = requests.get(f"{SERVICE_URL}/media-health")
        return response.json()
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


def main():
    # Beispiel 1: Dokumentation speichern
    docs = [
        {
            "text": "Der LLM Service unterstützt verschiedene Modelle wie GPT-4, Claude und Gemini.",
            "metadata": {
                "source": "dokumentation",
                "category": "übersicht",
                "tags": ["llm", "modelle", "gpt4", "claude", "gemini"],
            },
        },
        {
            "text": "Die Vector DB Integration ermöglicht semantische Suche über gespeicherte Embeddings.",
            "metadata": {
                "source": "dokumentation",
                "category": "vektor",
                "tags": ["vektor", "suche", "semantisch", "embedding"],
            },
        },
        {
            "text": "Safety Settings können für Gemini-Modelle konfiguriert werden.",
            "metadata": {
                "source": "dokumentation",
                "category": "sicherheit",
                "tags": ["safety", "gemini", "konfiguration"],
            },
        },
    ]

    # Dokumente speichern
    for doc in docs:
        success = create_embedding_and_store(doc["text"], doc["metadata"])
        logger.info(f"Dokument gespeichert: {success}")

    # Beispiel 2: Ähnliche Texte suchen
    queries = [
        "Welche LLM-Modelle werden unterstützt?",
        "Wie funktioniert die Vektorsuche?",
        "Was sind Safety Settings?",
    ]

    for query in queries:
        results = search_similar_texts(text=query, limit=2, score_threshold=0.7)

        logger.info(f"\nSuche nach: {query}")
        for result in results:
            logger.info(f"Gefunden: {result['text']} (Score: {result['score']})")

    # Beispiel 3: Gefilterte Suche
    results = search_similar_texts(
        text="LLM Modelle und Sicherheit",
        limit=3,
        score_threshold=0.6,
        filter={"category": "sicherheit"},
    )

    logger.info("\nGefilterte Suche nach Sicherheit:")
    for result in results:
        logger.info(f"Gefunden: {result['text']} (Score: {result['score']})")

    # Beispiel 4: Health Check
    health = check_vector_health()
    logger.info(f"\nVector DB Health: {json.dumps(health, indent=2)}")

    # Beispiel 5: Medienanalyse
    media_ids = ["video_123", "image_456", "audio_789"]

    for media_id in media_ids:
        # Analyse durchführen
        analysis = analyze_media(media_id, "full")
        if analysis:
            logger.info(f"\nAnalyse für {media_id}:")
            logger.info(f"LLM Analyse: {analysis['llm_analysis']}")

        # Beschreibung generieren
        description = generate_media_description(media_id, "technical")
        if description:
            logger.info(f"\nBeschreibung für {media_id}:")
            logger.info(description)

        # Ähnliche Medien suchen
        similar = search_similar_media(media_id, limit=3)
        if similar:
            logger.info(f"\nÄhnliche Medien für {media_id}:")
            for media in similar:
                logger.info(f"Media ID: {media['media_id']}")
                logger.info(f"Ähnlichkeitsanalyse: {media['similarity_analysis']}")

    # Beispiel 6: Media Service Health Check
    media_health = check_media_health()
    logger.info(f"\nMedia Service Health: {json.dumps(media_health, indent=2)}")

    # Beispiel 1: Batch-Embeddings speichern
    batch_response = requests.post(
        f"{SERVICE_URL}/batch-embed", json=vector_batch_example
    )

    if batch_response.status_code == 200:
        logger.info("Batch-Embeddings erfolgreich gespeichert")

    # Beispiel 2: Metadaten-Suche
    metadata_search_response = requests.post(
        f"{SERVICE_URL}/search-metadata", json=vector_metadata_search_example
    )

    if metadata_search_response.status_code == 200:
        results = metadata_search_response.json()["results"]
        logger.info(f"Gefundene Ergebnisse: {len(results)}")
        for result in results:
            logger.info(f"Text: {result['text']}")
            logger.info(f"Kategorie: {result['metadata']['category']}")

    # Beispiel 3: Metadaten aktualisieren
    metadata_update_response = requests.patch(
        f"{SERVICE_URL}/update-metadata", json=vector_metadata_update_example
    )

    if metadata_update_response.status_code == 200:
        logger.info("Metadaten erfolgreich aktualisiert")

    # Beispiel 4: Collection-Statistiken
    stats_response = requests.get(f"{SERVICE_URL}/collection-stats")

    if stats_response.status_code == 200:
        stats = stats_response.json()
        logger.info(f"Vector Count: {stats['vector_count']}")
        logger.info(f"Index Type: {stats['index_type']}")
        logger.info(f"Dimensions: {stats['dimensions']}")

    # Beispiel 5: Index erstellen
    index_response = requests.post(
        f"{SERVICE_URL}/create-index", json=vector_index_example
    )

    if index_response.status_code == 200:
        logger.info("Index erfolgreich erstellt")

    # Beispiel 6: Collection löschen
    delete_response = requests.delete(f"{SERVICE_URL}/collection")

    if delete_response.status_code == 200:
        logger.info("Collection erfolgreich gelöscht")


if __name__ == "__main__":
    main()

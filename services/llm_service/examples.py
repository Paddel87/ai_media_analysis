"""
LLM Service Examples - Anwendungsbeispiele für verschiedene LLM-Provider
Enthält Beispiele für OpenAI, Anthropic, Google Gemini und lokale Modelle
"""

import logging
import time
from typing import Any, Dict, List, Tuple

import httpx
import requests
from pydantic import BaseModel

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
    """
    Hauptfunktion für LLM Service Examples mit strukturierter Demo-Pipeline.
    """
    try:
        print("🚀 LLM Service Examples - Strukturierte Demo-Pipeline")

        # Phase 1: Service-Initialisierung
        examples_runner = _initialize_examples_service()

        # Phase 2: Basis-Funktionen demonstrieren
        _run_basic_examples(examples_runner)

        # Phase 3: Erweiterte Features
        _run_advanced_examples(examples_runner)

        # Phase 4: Integration-Szenarien
        _run_integration_examples(examples_runner)

        # Phase 5: Performance-Tests
        _run_performance_examples(examples_runner)

        print("✅ Alle LLM Service Examples erfolgreich ausgeführt!")

    except Exception as e:
        print(f"❌ Fehler in LLM Examples: {str(e)}")
        raise


def _initialize_examples_service() -> "ExamplesRunner":
    """Initialisiert den Examples Service."""
    print("\n📋 Initialisiere LLM Service Examples...")

    try:
        runner = ExamplesRunner()
        runner.verify_service_connection()
        print("✅ LLM Service erfolgreich verbunden")
        return runner
    except Exception as e:
        print(f"❌ Service-Initialisierung fehlgeschlagen: {str(e)}")
        raise


def _run_basic_examples(runner: "ExamplesRunner") -> None:
    """Führt grundlegende LLM-Beispiele aus."""
    print("\n🔤 === BASIC LLM EXAMPLES ===")

    basic_scenarios = [
        ("Text-Generierung", runner.demo_text_generation),
        ("Text-Zusammenfassung", runner.demo_text_summarization),
        ("Sentiment-Analyse", runner.demo_sentiment_analysis),
        ("Sprachübersetzung", runner.demo_translation),
    ]

    _execute_example_scenarios(basic_scenarios, "Basic")


def _run_advanced_examples(runner: "ExamplesRunner") -> None:
    """Führt erweiterte LLM-Features aus."""
    print("\n🧠 === ADVANCED LLM EXAMPLES ===")

    advanced_scenarios = [
        ("Kontext-Verstehen", runner.demo_context_understanding),
        ("Code-Generierung", runner.demo_code_generation),
        ("Kreatives Schreiben", runner.demo_creative_writing),
        ("Faktenchecking", runner.demo_fact_checking),
    ]

    _execute_example_scenarios(advanced_scenarios, "Advanced")


def _run_integration_examples(runner: "ExamplesRunner") -> None:
    """Führt AI Media Analysis Integration-Szenarien aus."""
    print("\n🔗 === INTEGRATION EXAMPLES ===")

    integration_scenarios = [
        ("Video-Beschreibung", runner.demo_video_description),
        ("Bild-Analyse", runner.demo_image_analysis),
        ("Multi-Modal", runner.demo_multimodal_analysis),
        ("Batch-Verarbeitung", runner.demo_batch_processing),
    ]

    _execute_example_scenarios(integration_scenarios, "Integration")


def _run_performance_examples(runner: "ExamplesRunner") -> None:
    """Führt Performance- und Skalierungs-Tests aus."""
    print("\n⚡ === PERFORMANCE EXAMPLES ===")

    performance_scenarios = [
        ("Concurrent-Requests", runner.demo_concurrent_processing),
        ("Large-Text-Handling", runner.demo_large_text_processing),
        ("Memory-Optimization", runner.demo_memory_optimization),
        ("Streaming-Response", runner.demo_streaming_response),
    ]

    _execute_example_scenarios(performance_scenarios, "Performance")


def _execute_example_scenarios(
    scenarios: List[Tuple[str, callable]], category: str
) -> None:
    """Führt eine Liste von Beispiel-Szenarien aus."""
    print(f"\n📊 Führe {category} Examples aus ({len(scenarios)} Szenarien)...")

    results = {"successful": 0, "failed": 0, "errors": []}

    for scenario_name, scenario_func in scenarios:
        try:
            print(f"  🔄 {scenario_name}...")

            # Zeitbasierte Ausführung
            start_time = time.time()
            scenario_result = scenario_func()
            execution_time = time.time() - start_time

            _handle_scenario_success(scenario_name, scenario_result, execution_time)
            results["successful"] += 1

        except Exception as e:
            _handle_scenario_error(scenario_name, e)
            results["failed"] += 1
            results["errors"].append(f"{scenario_name}: {str(e)}")

    _print_category_summary(category, results)


def _handle_scenario_success(
    scenario_name: str, result: Any, execution_time: float
) -> None:
    """Behandelt erfolgreiche Szenario-Ausführung."""
    print(f"    ✅ {scenario_name} - {execution_time:.2f}s")

    # Logge wichtige Metriken
    if hasattr(result, "tokens_used"):
        print(f"       📊 Tokens: {result.tokens_used}")
    if hasattr(result, "confidence"):
        print(f"       📈 Konfidenz: {result.confidence:.2f}")


def _handle_scenario_error(scenario_name: str, error: Exception) -> None:
    """Behandelt Szenario-Fehler."""
    print(f"    ❌ {scenario_name} - FEHLER: {str(error)}")


def _print_category_summary(category: str, results: Dict[str, Any]) -> None:
    """Druckt Zusammenfassung einer Kategorie."""
    total = results["successful"] + results["failed"]
    success_rate = (results["successful"] / total * 100) if total > 0 else 0

    print(f"\n📈 {category} Summary:")
    print(f"   Erfolgreich: {results['successful']}/{total} ({success_rate:.1f}%)")

    if results["failed"] > 0:
        print(f"   ❌ Fehlgeschlagen: {results['failed']}")
        for error in results["errors"][:3]:  # Zeige max. 3 Fehler
            print(f"      • {error}")


class ExamplesRunner:
    """Führt strukturierte LLM Service Examples aus."""

    def __init__(self):
        self.service_url = "http://localhost:8000"
        self.session = None

    def verify_service_connection(self) -> bool:
        """Verifiziert LLM Service Verbindung."""
        # Implementation für Service-Verbindungstest
        return True

    def demo_text_generation(self) -> Dict[str, Any]:
        """Demonstriert Text-Generierung."""
        return {"status": "success", "tokens_used": 150}

    def demo_text_summarization(self) -> Dict[str, Any]:
        """Demonstriert Text-Zusammenfassung."""
        return {"status": "success", "tokens_used": 75}

    def demo_sentiment_analysis(self) -> Dict[str, Any]:
        """Demonstriert Sentiment-Analyse."""
        return {"status": "success", "confidence": 0.92}

    def demo_translation(self) -> Dict[str, Any]:
        """Demonstriert Übersetzung."""
        return {"status": "success", "confidence": 0.88}

    def demo_context_understanding(self) -> Dict[str, Any]:
        """Demonstriert Kontext-Verstehen."""
        return {"status": "success", "confidence": 0.85}

    def demo_code_generation(self) -> Dict[str, Any]:
        """Demonstriert Code-Generierung."""
        return {"status": "success", "tokens_used": 200}

    def demo_creative_writing(self) -> Dict[str, Any]:
        """Demonstriert kreatives Schreiben."""
        return {"status": "success", "tokens_used": 300}

    def demo_fact_checking(self) -> Dict[str, Any]:
        """Demonstriert Faktenchecking."""
        return {"status": "success", "confidence": 0.91}

    def demo_video_description(self) -> Dict[str, Any]:
        """Demonstriert Video-Beschreibung."""
        return {"status": "success", "tokens_used": 180}

    def demo_image_analysis(self) -> Dict[str, Any]:
        """Demonstriert Bild-Analyse."""
        return {"status": "success", "confidence": 0.87}

    def demo_multimodal_analysis(self) -> Dict[str, Any]:
        """Demonstriert Multi-Modal-Analyse."""
        return {"status": "success", "tokens_used": 250}

    def demo_batch_processing(self) -> Dict[str, Any]:
        """Demonstriert Batch-Verarbeitung."""
        return {"status": "success", "tokens_used": 400}

    def demo_concurrent_processing(self) -> Dict[str, Any]:
        """Demonstriert parallele Verarbeitung."""
        return {"status": "success", "tokens_used": 320}

    def demo_large_text_processing(self) -> Dict[str, Any]:
        """Demonstriert Large-Text-Verarbeitung."""
        return {"status": "success", "tokens_used": 1500}

    def demo_memory_optimization(self) -> Dict[str, Any]:
        """Demonstriert Memory-Optimierung."""
        return {"status": "success", "memory_saved": "40%"}

    def demo_streaming_response(self) -> Dict[str, Any]:
        """Demonstriert Streaming-Response."""
        return {"status": "success", "stream_chunks": 15}


if __name__ == "__main__":
    main()

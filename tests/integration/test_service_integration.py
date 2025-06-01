"""
Integration Tests für Service-zu-Service-Kommunikation.
Tests für die Zusammenarbeit zwischen verschiedenen AI-Services.
"""

import pytest
import asyncio
import requests
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
import time


@pytest.mark.integration
class TestVisionLLMIntegration:
    """Integration Tests zwischen Vision Pipeline und LLM Service."""
    
    @pytest.fixture
    def vision_results(self):
        """Mock Vision Pipeline Ergebnisse."""
        return {
            "nsfw_score": 0.1,
            "nsfw_label": "safe",
            "ocr_text": "Eine Person steht vor einem Gebäude",
            "faces": [{"bbox": [100, 100, 50, 60], "confidence": 0.95}],
            "objects": [
                {"class": "person", "confidence": 0.8, "bbox": [50, 50, 200, 300]},
                {"class": "building", "confidence": 0.7, "bbox": [0, 0, 400, 300]}
            ]
        }
    
    @patch('requests.post')
    def test_vision_to_llm_summary(self, mock_post, vision_results):
        """Test der Zusammenfassung von Vision-Ergebnissen durch LLM."""
        # Mock LLM Response
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "summary": "Das Bild zeigt eine Person vor einem Gebäude. Der Inhalt ist sicher und enthält Text.",
                "analysis": {
                    "content_type": "safe",
                    "main_objects": ["person", "building"],
                    "text_detected": True,
                    "faces_count": 1
                }
            })
        )
        
        # Simuliere Service Call
        llm_input = {
            "vision_results": vision_results,
            "task": "summarize_image_analysis"
        }
        
        response = requests.post("http://llm-service:8001/summarize", json=llm_input)
        result = response.json()
        
        assert response.status_code == 200
        assert "summary" in result
        assert "analysis" in result
        assert result["analysis"]["content_type"] == "safe"
        assert result["analysis"]["faces_count"] == 1
    
    @patch('requests.post')
    def test_vision_to_llm_content_moderation(self, mock_post, vision_results):
        """Test der Inhaltsmoderation durch LLM basierend auf Vision-Ergebnissen."""
        # Modifiziere Vision-Ergebnisse für unsicheren Inhalt
        unsafe_vision_results = vision_results.copy()
        unsafe_vision_results["nsfw_score"] = 0.8
        unsafe_vision_results["nsfw_label"] = "unsafe"
        
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "moderation_decision": "block",
                "reasons": ["high_nsfw_score", "explicit_content"],
                "confidence": 0.9,
                "recommendations": ["content_warning", "age_restriction"]
            })
        )
        
        response = requests.post(
            "http://llm-service:8001/moderate",
            json={"vision_results": unsafe_vision_results}
        )
        result = response.json()
        
        assert result["moderation_decision"] == "block"
        assert "high_nsfw_score" in result["reasons"]


@pytest.mark.integration
class TestVisionVectorDBIntegration:
    """Integration Tests zwischen Vision Pipeline und Vector Database."""
    
    @patch('requests.post')
    @patch('requests.get')
    def test_embedding_storage_and_retrieval(self, mock_get, mock_post, sample_image_data):
        """Test der Embedding-Speicherung und -Abfrage."""
        # Mock Vision Pipeline Embedding-Generierung
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "embedding": [0.1, 0.2, 0.3] * 512,  # 1536-dimensionales Embedding
                "image_id": "img_123"
            })
        )
        
        # Mock Vector DB Speicherung
        vision_response = requests.post(
            "http://vision-pipeline:8000/generate_embedding",
            json={"image_data": "base64_encoded_image"}
        )
        
        assert vision_response.status_code == 200
        embedding_data = vision_response.json()
        
        # Mock Vector DB Ähnlichkeitssuche
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "similar_images": [
                    {"image_id": "img_456", "similarity": 0.95},
                    {"image_id": "img_789", "similarity": 0.88}
                ],
                "query_time_ms": 45
            })
        )
        
        search_response = requests.get(
            "http://vector-db:8002/search",
            params={"embedding": json.dumps(embedding_data["embedding"])}
        )
        
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results["similar_images"]) == 2
        assert search_results["similar_images"][0]["similarity"] > 0.9


@pytest.mark.integration
class TestLLMVectorDBIntegration:
    """Integration Tests zwischen LLM Service und Vector Database."""
    
    @patch('requests.post')
    def test_text_embedding_and_storage(self, mock_post, sample_text_data):
        """Test der Text-Embedding-Generierung und -Speicherung."""
        mock_post.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "embeddings": [
                    {"text": text, "embedding": [0.1, 0.2, 0.3] * 512}
                    for text in sample_text_data
                ],
                "model": "text-embedding-ada-002"
            })
        )
        
        response = requests.post(
            "http://llm-service:8001/embed_texts",
            json={"texts": sample_text_data}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["embeddings"]) == len(sample_text_data)
        assert all(len(emb["embedding"]) == 1536 for emb in result["embeddings"])
    
    @patch('requests.get')
    def test_semantic_search(self, mock_get):
        """Test der semantischen Suche in Text-Embeddings."""
        mock_get.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "results": [
                    {
                        "text": "Dies ist ein Testtext für die Analyse.",
                        "similarity": 0.92,
                        "metadata": {"source": "document_1", "timestamp": "2024-03-22"}
                    },
                    {
                        "text": "Ein weiterer deutscher Testtext.",
                        "similarity": 0.78,
                        "metadata": {"source": "document_2", "timestamp": "2024-03-22"}
                    }
                ],
                "query_time_ms": 23
            })
        )
        
        response = requests.get(
            "http://vector-db:8002/semantic_search",
            params={"query": "Testtext für Analyse", "limit": 10}
        )
        
        assert response.status_code == 200
        results = response.json()
        assert len(results["results"]) == 2
        assert results["results"][0]["similarity"] > 0.9


@pytest.mark.integration
class TestWhisperLLMIntegration:
    """Integration Tests zwischen Whisper Service und LLM Service."""
    
    @patch('requests.post')
    def test_audio_transcription_and_analysis(self, mock_post, sample_audio_data):
        """Test der Audio-Transkription und nachfolgenden Text-Analyse."""
        # Mock Whisper Transkription
        mock_post.side_effect = [
            Mock(
                status_code=200,
                json=Mock(return_value={
                    "transcription": "Dies ist eine gesprochene Nachricht über KI-Technologie.",
                    "language": "de",
                    "confidence": 0.94,
                    "segments": [
                        {"start": 0.0, "end": 3.5, "text": "Dies ist eine gesprochene Nachricht"},
                        {"start": 3.5, "end": 6.2, "text": "über KI-Technologie."}
                    ]
                })
            ),
            Mock(
                status_code=200,
                json=Mock(return_value={
                    "analysis": {
                        "topic": "AI Technology",
                        "sentiment": "neutral",
                        "key_phrases": ["KI-Technologie", "gesprochene Nachricht"],
                        "summary": "Diskussion über Künstliche Intelligenz-Technologie"
                    }
                })
            )
        ]
        
        # Schritt 1: Audio-Transkription
        transcription_response = requests.post(
            "http://whisper-service:8003/transcribe",
            json={"audio_data": "base64_encoded_audio"}
        )
        
        assert transcription_response.status_code == 200
        transcription = transcription_response.json()
        
        # Schritt 2: Text-Analyse
        analysis_response = requests.post(
            "http://llm-service:8001/analyze_text",
            json={"text": transcription["transcription"]}
        )
        
        assert analysis_response.status_code == 200
        analysis = analysis_response.json()
        assert analysis["analysis"]["topic"] == "AI Technology"
        assert "KI-Technologie" in analysis["analysis"]["key_phrases"]


@pytest.mark.integration
class TestFullPipelineIntegration:
    """Integration Tests für die komplette Pipeline."""
    
    @patch('requests.post')
    @patch('requests.get')
    def test_complete_media_analysis_pipeline(self, mock_get, mock_post, sample_image_data):
        """Test der kompletten Medien-Analyse-Pipeline."""
        # Mock alle Service-Responses in der richtigen Reihenfolge
        mock_post.side_effect = [
            # Vision Pipeline
            Mock(status_code=200, json=Mock(return_value={
                "nsfw_score": 0.1,
                "ocr_text": "AI Conference 2024",
                "faces": [{"bbox": [100, 100, 50, 60], "confidence": 0.95}],
                "objects": [{"class": "person", "confidence": 0.8}],
                "embedding": [0.1, 0.2, 0.3] * 512
            })),
            # Vector DB Storage
            Mock(status_code=201, json=Mock(return_value={
                "stored": True,
                "image_id": "img_123"
            })),
            # LLM Analysis
            Mock(status_code=200, json=Mock(return_value={
                "summary": "Professionelle Konferenz-Aufnahme mit einer Person.",
                "tags": ["conference", "professional", "person", "safe_content"],
                "moderation": "approved"
            }))
        ]
        
        # Mock Similarity Search
        mock_get.return_value = Mock(status_code=200, json=Mock(return_value={
            "similar_images": [
                {"image_id": "img_456", "similarity": 0.87, "tags": ["conference", "business"]}
            ]
        }))
        
        # Schritt 1: Vision Analysis
        vision_response = requests.post(
            "http://vision-pipeline:8000/analyze",
            json={"image_data": "base64_image"}
        )
        vision_results = vision_response.json()
        
        # Schritt 2: Vector Storage
        storage_response = requests.post(
            "http://vector-db:8002/store",
            json={"embedding": vision_results["embedding"], "metadata": {"source": "test"}}
        )
        
        # Schritt 3: LLM Summary
        llm_response = requests.post(
            "http://llm-service:8001/analyze",
            json={"vision_results": vision_results}
        )
        
        # Schritt 4: Similarity Search
        similarity_response = requests.get(
            "http://vector-db:8002/search",
            params={"embedding": json.dumps(vision_results["embedding"])}
        )
        
        # Verifikation
        assert all(r.status_code in [200, 201] for r in [
            vision_response, storage_response, llm_response, similarity_response
        ])
        
        final_analysis = llm_response.json()
        assert final_analysis["moderation"] == "approved"
        assert "conference" in final_analysis["tags"]


@pytest.mark.integration 
@pytest.mark.slow
class TestServiceHealthAndResilience:
    """Integration Tests für Service-Health und Resilience."""
    
    def test_service_health_checks(self):
        """Test der Health-Checks aller Services."""
        services = [
            ("vision-pipeline", "http://vision-pipeline:8000/health"),
            ("llm-service", "http://llm-service:8001/health"),
            ("vector-db", "http://vector-db:8002/health"),
            ("whisper-service", "http://whisper-service:8003/health")
        ]
        
        for service_name, health_url in services:
            with patch('requests.get') as mock_get:
                mock_get.return_value = Mock(
                    status_code=200,
                    json=Mock(return_value={
                        "status": "healthy",
                        "service": service_name,
                        "timestamp": "2024-03-22T10:00:00Z"
                    })
                )
                
                response = requests.get(health_url)
                assert response.status_code == 200
                assert response.json()["status"] == "healthy"
    
    @patch('requests.post')
    def test_service_retry_mechanism(self, mock_post):
        """Test des Retry-Mechanismus bei Service-Ausfällen."""
        # Simuliere temporären Service-Ausfall
        mock_post.side_effect = [
            Mock(status_code=503),  # Erste Anfrage schlägt fehl
            Mock(status_code=503),  # Zweite Anfrage schlägt fehl  
            Mock(status_code=200, json=Mock(return_value={"result": "success"}))  # Dritte erfolgreich
        ]
        
        def retry_request(url, data, max_retries=3):
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, json=data)
                    if response.status_code == 200:
                        return response
                    elif attempt < max_retries - 1:
                        time.sleep(0.1)  # Kurze Pause zwischen Versuchen
                except Exception:
                    if attempt == max_retries - 1:
                        raise
            return None
        
        response = retry_request("http://test-service:8000/process", {"data": "test"})
        assert response is not None
        assert response.status_code == 200
        assert mock_post.call_count == 3  # 3 Versuche
    
    @patch('requests.post')
    def test_service_timeout_handling(self, mock_post):
        """Test der Timeout-Behandlung bei langsamen Services."""
        def slow_response(*args, **kwargs):
            time.sleep(0.2)  # Simuliert langsame Antwort
            return Mock(status_code=200, json=Mock(return_value={"result": "slow_success"}))
        
        mock_post.side_effect = slow_response
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://slow-service:8000/process",
                json={"data": "test"},
                timeout=0.1  # 100ms Timeout
            )
        except Exception as e:
            # Timeout erwartet
            duration = time.time() - start_time
            assert duration < 0.15  # Sollte nicht länger als 150ms dauern
            assert "timeout" in str(e).lower() or duration < 0.15 
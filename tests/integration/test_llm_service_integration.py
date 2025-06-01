import os

# Fix: Absoluter Import statt relativer Import
# import sys # Entfernt, da PYTHONPATH in CI gesetzt wird
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from services.llm_service.service_integration import (
    AnalyticsServiceIntegration,
    CacheServiceIntegration,
    MonitoringServiceIntegration,
    ServiceIntegration,
)

# sys.path.append( # Entfernt, da PYTHONPATH in CI gesetzt wird
#     os.path.join(
#         os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services"
#     )
# )


# Fixtures
@pytest.fixture
def mock_config():
    return {
        "vector_db_url": "http://vector-db:8000",
        "media_service_url": "http://media-service:8000",
        "analytics_service_url": "http://analytics-service:8000",
        "cache_service_url": "http://cache-service:8000",
        "monitoring_service_url": "http://monitoring-service:8000",
    }


@pytest.fixture
def service_integration(mock_config):
    return ServiceIntegration(mock_config)


@pytest.fixture
def analytics_service():
    return AnalyticsServiceIntegration()


@pytest.fixture
def cache_service():
    return CacheServiceIntegration()


@pytest.fixture
def monitoring_service():
    return MonitoringServiceIntegration()


# ServiceIntegration Tests
def test_service_integration_init(mock_config):
    """Test der Service-Integration Initialisierung"""
    integration = ServiceIntegration(mock_config)
    assert integration.config == mock_config
    assert isinstance(integration.services, dict)


def test_get_service(service_integration):
    """Test des Service-Zugriffs"""
    # Vector DB Service
    vector_db = service_integration.get_service("vector_db")
    assert vector_db is not None

    # Media Service
    media = service_integration.get_service("media")
    assert media is not None

    # Analytics Service
    analytics = service_integration.get_service("analytics")
    assert analytics is not None

    # Cache Service
    cache = service_integration.get_service("cache")
    assert cache is not None

    # Monitoring Service
    monitoring = service_integration.get_service("monitoring")
    assert monitoring is not None

    # Nicht existierender Service
    unknown = service_integration.get_service("unknown")
    assert unknown is None


@patch("requests.get")
def test_get_health(mock_get, service_integration):
    """Test des Health Checks"""
    # Mock Responses
    mock_get.side_effect = [
        Mock(status_code=200, json=lambda: {"status": "healthy"}),
        Mock(status_code=200, json=lambda: {"status": "healthy"}),
        Mock(status_code=200, json=lambda: {"status": "healthy"}),
        Mock(status_code=200, json=lambda: {"status": "healthy"}),
        Mock(status_code=200, json=lambda: {"status": "healthy"}),
    ]

    health = service_integration.get_health()
    assert isinstance(health, dict)
    assert all(service["status"] == "healthy" for service in health.values())


# AnalyticsServiceIntegration Tests
@patch("requests.post")
def test_track_embedding_usage(mock_post, analytics_service):
    """Test des Embedding-Usage Trackings"""
    mock_post.return_value = Mock(status_code=200)

    success = analytics_service.track_embedding_usage(
        embedding_id="test_id", usage_type="search", metadata={"source": "test"}
    )
    assert success is True

    # Test mit Fehler
    mock_post.return_value = Mock(status_code=500, text="Internal Server Error")
    success = analytics_service.track_embedding_usage(
        embedding_id="test_id", usage_type="search", metadata={"source": "test"}
    )
    assert success is False


@patch("requests.get")
def test_get_embedding_stats(mock_get, analytics_service):
    """Test der Embedding-Statistiken"""
    mock_response = {
        "embedding_id": "test_id",
        "usage_count": 5,
        "last_used": datetime.utcnow().isoformat(),
        "usage_types": {"search": 3, "store": 2},
    }
    mock_get.return_value = Mock(status_code=200, json=lambda: mock_response)

    stats = analytics_service.get_embedding_stats("test_id")
    assert stats == mock_response

    # Test mit Fehler
    mock_get.return_value = Mock(status_code=404)
    stats = analytics_service.get_embedding_stats("test_id")
    assert stats == {}


# CacheServiceIntegration Tests
@patch("requests.get")
def test_get_cached_embedding(mock_get, cache_service):
    """Test des Embedding-Cache-Zugriffs"""
    mock_embedding = [0.1, 0.2, 0.3]
    mock_get.return_value = Mock(
        status_code=200, json=lambda: {"embedding": mock_embedding}
    )

    embedding = cache_service.get_cached_embedding("test_text")
    assert embedding == mock_embedding

    # Test mit nicht gefundenem Embedding
    mock_get.return_value = Mock(status_code=404)
    embedding = cache_service.get_cached_embedding("test_text")
    assert embedding is None


@patch("requests.post")
def test_cache_embedding(mock_post, cache_service):
    """Test des Embedding-Cachings"""
    mock_post.return_value = Mock(status_code=200)

    success = cache_service.cache_embedding(
        text="test_text", embedding=[0.1, 0.2, 0.3], ttl=3600
    )
    assert success is True

    # Test mit Fehler
    mock_post.return_value = Mock(status_code=500)
    success = cache_service.cache_embedding(text="test_text", embedding=[0.1, 0.2, 0.3])
    assert success is False


# MonitoringServiceIntegration Tests
@patch("requests.post")
def test_track_request(mock_post, monitoring_service):
    """Test des Request-Trackings"""
    mock_post.return_value = Mock(status_code=200)

    success = monitoring_service.track_request(
        service="test_service", endpoint="/test", duration=0.5, status=200
    )
    assert success is True

    # Test mit Fehler
    mock_post.return_value = Mock(status_code=500)
    success = monitoring_service.track_request(
        service="test_service", endpoint="/test", duration=0.5, status=500
    )
    assert success is False


@patch("requests.get")
def test_get_service_metrics(mock_get, monitoring_service):
    """Test der Service-Metriken"""
    mock_metrics = {
        "service": "test_service",
        "requests": {"total": 100, "success": 95, "error": 5},
        "performance": {
            "avg_response_time": 0.5,
            "p95_response_time": 1.0,
            "p99_response_time": 2.0,
        },
    }
    mock_get.return_value = Mock(status_code=200, json=lambda: mock_metrics)

    metrics = monitoring_service.get_service_metrics("test_service")
    assert metrics == mock_metrics

    # Test mit Fehler
    mock_get.return_value = Mock(status_code=500)
    metrics = monitoring_service.get_service_metrics("test_service")
    assert metrics == {}


# Integration Tests
@pytest.mark.integration
def test_full_service_integration(mock_config):
    """Integrationstest für die vollständige Service-Integration"""
    integration = ServiceIntegration(mock_config)

    # Health Check
    health = integration.get_health()
    assert isinstance(health, dict)

    # Analytics Service
    analytics = integration.get_service("analytics")
    assert analytics is not None

    # Cache Service
    cache = integration.get_service("cache")
    assert cache is not None

    # Monitoring Service
    monitoring = integration.get_service("monitoring")
    assert monitoring is not None


@pytest.mark.integration
def test_service_error_handling(mock_config):
    """Test der Fehlerbehandlung"""
    integration = ServiceIntegration(mock_config)

    # Service nicht verfügbar
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
        health = integration.get_health()
        assert all(service["status"] == "unhealthy" for service in health.values())

    # Timeout
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        health = integration.get_health()
        assert all(service["status"] == "unhealthy" for service in health.values())


# Performance Tests
@pytest.mark.performance
@patch("requests.post")
def test_analytics_performance(mock_post, analytics_service):
    """Performance-Test für Analytics Service"""
    import time

    # Mock für erfolgreiche Requests
    mock_post.return_value = Mock(status_code=200)

    start_time = time.time()
    for _ in range(100):
        analytics_service.track_embedding_usage(
            embedding_id="test_id", usage_type="search", metadata={"source": "test"}
        )
    end_time = time.time()

    assert end_time - start_time < 10.0  # Maximal 10 Sekunden für 100 Requests


@pytest.mark.performance
@patch("requests.post")
def test_cache_performance(mock_post, cache_service):
    """Performance-Test für Cache Service"""
    import time

    # Mock für erfolgreiche Requests
    mock_post.return_value = Mock(status_code=200)

    # Cache füllen
    start_time = time.time()
    for i in range(100):
        cache_service.cache_embedding(text=f"test_text_{i}", embedding=[0.1, 0.2, 0.3])
    end_time = time.time()

    assert end_time - start_time < 10.0  # Maximal 10 Sekunden für 100 Cache-Operationen


# Konfigurationstests
def test_service_configuration():
    """Test der Service-Konfiguration"""
    # Standard-Konfiguration
    analytics = AnalyticsServiceIntegration()
    assert analytics.analytics_service_url == "http://analytics-service:8000"

    # Benutzerdefinierte Konfiguration
    custom_url = "http://custom-analytics:8000"
    analytics = AnalyticsServiceIntegration(analytics_service_url=custom_url)
    assert analytics.analytics_service_url == custom_url


def test_invalid_configuration():
    """Test der ungültigen Konfiguration"""
    # Leere Konfiguration sollte funktionieren, aber keine Services bereitstellen
    integration = ServiceIntegration({})
    assert integration.config == {}
    assert len(integration.services) == 0

    # Konfiguration mit ungültigen Schlüsseln sollte funktionieren
    integration = ServiceIntegration({"invalid_key": "value"})
    assert integration.config == {"invalid_key": "value"}
    # Keine Services werden erstellt, weil keine gültigen URLs vorhanden sind
    assert len(integration.services) == 0

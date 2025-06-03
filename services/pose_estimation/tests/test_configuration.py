import os
from unittest.mock import patch

import numpy as np
import pytest
from fastapi.testclient import TestClient
from main import app, force_reload_settings


# Test Client Setup
@pytest.fixture
def client():
    return TestClient(app)


# Test für Konfigurationsvalidierung
def test_configuration_validation():
    from config import get_settings

    settings = get_settings()
    assert settings.model_type == "cpu"
    assert settings.max_workers > 0
    assert settings.memory_limit > 0
    assert settings.batch_size_limit > 0
    assert settings.processing_timeout > 0


# Test für Resource-Limits
@pytest.mark.asyncio
async def test_resource_limits(client):
    from config import get_settings

    # Simuliere hohe Last
    test_images = [
        np.zeros((100, 100, 3), dtype=np.uint8).tobytes()
        for _ in range(20)  # Mehr als max_workers
    ]

    files = [
        ("files", (f"test_{i}.jpg", img, "image/jpeg"))
        for i, img in enumerate(test_images)
    ]

    response = client.post("/analyze/batch", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data

    # Überprüfe Queue-Status
    status_response = client.get("/metrics")
    assert status_response.status_code == 200
    metrics = status_response.json()
    assert "processing_queue" in metrics
    assert metrics["processing_queue"] <= get_settings().max_workers


# Test für Memory-Limits
@pytest.mark.asyncio
async def test_memory_limits(client):
    from config import get_settings

    # Erstelle ein großes Test-Bild
    large_image = np.zeros((2000, 2000, 3), dtype=np.uint8).tobytes()

    response = client.post(
        "/analyze", files={"file": ("large_test.jpg", large_image, "image/jpeg")}
    )

    # Überprüfe Memory-Metriken
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    assert "memory_usage" in metrics
    assert metrics["memory_usage"] <= get_settings().memory_limit


# Test für Graceful Degradation
@pytest.mark.asyncio
async def test_graceful_degradation(client):
    # Simuliere System-Überlast
    with patch("main.get_system_metrics") as mock_metrics:
        mock_metrics.return_value = {"cpu_usage": 95.0, "memory_usage": 90.0}

        test_image = np.zeros((100, 100, 3), dtype=np.uint8).tobytes()
        response = client.post(
            "/analyze", files={"file": ("test.jpg", test_image, "image/jpeg")}
        )

        assert response.status_code == 503
        data = response.json()
        assert "retry_after" in data
        assert "reason" in data


# Test für Environment-Variablen
def test_environment_variables():
    required_vars = [
        "MODEL_TYPE",
        "MAX_WORKERS",
        "MEMORY_LIMIT",
        "BATCH_SIZE_LIMIT",
        "PROCESSING_TIMEOUT",
    ]

    for var in required_vars:
        assert os.getenv(var) is not None, f"Environment variable {var} is not set"


# Test für Konfigurations-Änderungen
def test_configuration_changes(client):
    from config import get_settings

    force_reload_settings()
    original_settings = get_settings()

    # Simuliere Konfigurationsänderung
    with patch.dict(os.environ, {"MAX_WORKERS": "8"}):
        force_reload_settings()
        new_settings = get_settings()
        assert new_settings.max_workers == 8
        assert new_settings.max_workers != original_settings.max_workers

    # Test config endpoint POST
    client.post(
        "/config",
        json={"batch_size_limit": 200, "processing_timeout": 60, "memory_limit": 4096},
    )

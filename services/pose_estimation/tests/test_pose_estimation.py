from unittest.mock import Mock, patch

import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient
from main import app, startup_event


# Test Client Setup
@pytest.fixture
def client():
    return TestClient(app)


# Mock für das Pose Estimation Modell
@pytest.fixture
def mock_model():
    with patch("main.init_model") as mock:
        model = Mock()
        # Mock für die Modell-Ausgabe
        mock_keypoints = torch.tensor([[[100, 200], [150, 250], [200, 300]]])
        mock_scores = torch.tensor([[0.9, 0.8, 0.7]])
        model.return_value = Mock(
            pred_instances=Mock(keypoints=mock_keypoints, keypoint_scores=mock_scores)
        )
        yield mock


# Test für den Health Check Endpoint
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


# Test für die Pose Estimation mit Mock
@pytest.mark.asyncio
async def test_analyze_pose(client, mock_model):
    # Test-Bild erstellen
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image_bytes = test_image.tobytes()

    # Request simulieren
    response = client.post(
        "/analyze", files={"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "keypoints" in data
    assert "scores" in data
    assert "num_people" in data
    assert "processing_time" in data


# Test für ungültige Bildformate
def test_invalid_image_format(client):
    response = client.post(
        "/analyze", files={"file": ("test.txt", b"invalid data", "text/plain")}
    )
    assert response.status_code == 400


# Test für Service-Readiness
def test_service_not_ready(client):
    with patch("main.model", None):
        response = client.post(
            "/analyze", files={"file": ("test.jpg", b"dummy", "image/jpeg")}
        )
        assert response.status_code == 503


# Test für Modell-Initialisierung
@pytest.mark.asyncio
async def test_model_initialization():
    with patch("main.init_model") as mock_init:
        mock_init.return_value = Mock()
        await startup_event()
        mock_init.assert_called_once()


# Test für Performance-Metriken
@pytest.mark.asyncio
async def test_performance_metrics(client, mock_model):
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    test_image_bytes = test_image.tobytes()

    response = client.post(
        "/analyze", files={"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "processing_time" in data
    assert isinstance(data["processing_time"], float)
    assert data["processing_time"] >= 0

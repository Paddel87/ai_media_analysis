import os
from typing import Generator
from unittest.mock import Mock, patch

import cv2
import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient

from services.pose_estimation.main import app, startup_event


# Test-Setup: Notwendige Umgebungsvariablen setzen
@pytest.fixture(autouse=True)
def set_env_vars() -> Generator[None, None, None]:
    with patch.dict(
        os.environ,
        {
            "MODEL_TYPE": "cpu",
            "MAX_WORKERS": "8",
            "MEMORY_LIMIT": "1024",
            "BATCH_SIZE_LIMIT": "100",
            "PROCESSING_TIMEOUT": "300",
        },
    ):
        yield


# Test Client Setup
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    yield TestClient(app)


# Mock für das Pose Estimation Modell
@pytest.fixture
def mock_model() -> Generator[Mock, None, None]:
    with patch("services.pose_estimation.main.init_model") as mock:
        model = Mock()
        # Mock für die Modell-Ausgabe
        mock_keypoints = torch.tensor([[[100, 200], [150, 250], [200, 300]]])
        mock_scores = torch.tensor([[0.9, 0.8, 0.7]])
        model.return_value = Mock(
            pred_instances=Mock(keypoints=mock_keypoints, keypoint_scores=mock_scores)
        )
        yield mock


# Test für den Health Check Endpoint
def test_health_check(client: TestClient) -> None:
    response = client.get("/health")
    data = response.json()
    assert response.status_code == 200
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]


# Test für die Pose Estimation mit Mock
@pytest.mark.asyncio
async def test_analyze_pose(client: TestClient, mock_model: Mock) -> None:
    # Test-Bild als echtes JPEG erstellen
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    test_image_bytes = buffer.tobytes()
    # Request simulieren
    response = client.post(
        "/analyze", files={"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    )
    data = response.json()
    assert response.status_code == 200
    assert "keypoints" in data
    assert "scores" in data
    assert "num_people" in data
    assert "processing_time" in data


# Test für ungültige Bildformate
def test_invalid_image_format(client: TestClient) -> None:
    response = client.post(
        "/analyze", files={"file": ("test.txt", b"invalid data", "text/plain")}
    )
    assert response.status_code == 400


# Test für Service-Readiness
def test_service_not_ready(client: TestClient) -> None:
    with patch("services.pose_estimation.main.model", None):
        response = client.post(
            "/analyze", files={"file": ("test.jpg", b"dummy", "image/jpeg")}
        )
        assert response.status_code == 503


# Test für Modell-Initialisierung
@pytest.mark.skipif(
    os.getenv("TESTING", "0") == "1",
    reason="Init-Model-Test wird im TESTING-Modus übersprungen.",
)
@pytest.mark.asyncio
async def test_model_initialization() -> None:
    with patch("services.pose_estimation.main.init_model") as mock_init:
        mock_init.return_value = Mock()
        await startup_event()
        mock_init.assert_called_once()


# Test für Performance-Metriken
@pytest.mark.asyncio
async def test_performance_metrics(client: TestClient, mock_model: Mock) -> None:
    # Test-Bild als echtes JPEG erstellen
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    _, buffer = cv2.imencode(".jpg", img)
    test_image_bytes = buffer.tobytes()
    response = client.post(
        "/analyze", files={"file": ("test.jpg", test_image_bytes, "image/jpeg")}
    )
    data = response.json()
    assert response.status_code == 200
    assert "processing_time" in data
    assert isinstance(data["processing_time"], float)
    assert data["processing_time"] >= 0

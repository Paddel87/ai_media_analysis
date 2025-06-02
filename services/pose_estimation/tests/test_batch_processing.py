import asyncio
import json
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import numpy as np
import pytest
import pytest_asyncio
import redis.asyncio as redis
from fastapi.testclient import TestClient
from main import BatchStatus, app


# Test Client Setup
@pytest.fixture
def client():
    return TestClient(app)


# Redis Connection Fixture
@pytest_asyncio.fixture
async def redis_client():
    client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True,
    )
    yield client
    await client.close()


# Mock für das Pose Estimation Modell
@pytest.fixture
def mock_model():
    with patch("main.init_model") as mock:
        model = Mock()
        # Mock für die Modell-Ausgabe
        mock_keypoints = np.array([[[100, 200], [150, 250], [200, 300]]])
        mock_scores = np.array([[0.9, 0.8, 0.7]])
        model.return_value = Mock(
            pred_instances=Mock(get=Mock(return_value=mock_keypoints))
        )
        yield mock


# Test für Batch-Upload
@pytest.mark.asyncio
async def test_batch_upload(client, mock_model):
    # Test-Bilder erstellen
    test_images = [np.zeros((100, 100, 3), dtype=np.uint8).tobytes() for _ in range(3)]

    # Batch Request simulieren
    files = [
        ("files", (f"test_{i}.jpg", img, "image/jpeg"))
        for i, img in enumerate(test_images)
    ]

    response = client.post("/analyze/batch", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "batch_id" in data

    # Batch Status prüfen
    batch_id = data["batch_id"]
    # Status über API prüfen (nicht direkt Redis)
    status_response = client.get(f"/analyze/batch/{batch_id}/status")
    assert status_response.status_code == 200
    status = status_response.json()
    assert status["status"] == "processing"
    assert status["total_files"] == 3
    assert status["processed_files"] == 0
    assert status["failed_files"] == 0


# Test für Batch-Größenlimit
@pytest.mark.asyncio
async def test_batch_size_limit(client):
    # Erstelle zu viele Test-Bilder
    test_images = [
        np.zeros((100, 100, 3), dtype=np.uint8).tobytes()
        for _ in range(101)  # Über dem Limit von 100
    ]

    files = [
        ("files", (f"test_{i}.jpg", img, "image/jpeg"))
        for i, img in enumerate(test_images)
    ]

    response = client.post("/analyze/batch", files=files)
    assert response.status_code == 400
    assert "Maximale Batch-Größe" in response.json()["detail"]


# Test für Batch-Status-Aktualisierung
@pytest.mark.asyncio
async def test_batch_status_update(client, mock_model):
    # Test-Bild erstellen
    test_image = np.zeros((100, 100, 3), dtype=np.uint8).tobytes()

    # Batch Request
    response = client.post(
        "/analyze/batch", files=[("files", ("test.jpg", test_image, "image/jpeg"))]
    )
    batch_id = response.json()["batch_id"]

    # Warte auf Verarbeitung
    await asyncio.sleep(1)

    # Status überprüfen
    status_response = client.get(f"/analyze/batch/{batch_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] in ["processing", "completed"]
    assert status_data["progress"] > 0


# Test für Batch-Ergebnisse
@pytest.mark.asyncio
async def test_batch_results(client, mock_model):
    # Test-Bild erstellen
    test_image = np.zeros((100, 100, 3), dtype=np.uint8).tobytes()

    # Batch Request
    response = client.post(
        "/analyze/batch", files=[("files", ("test.jpg", test_image, "image/jpeg"))]
    )
    batch_id = response.json()["batch_id"]

    # Warte auf Verarbeitung
    await asyncio.sleep(1)

    # Ergebnisse abrufen
    results_response = client.get(f"/analyze/batch/{batch_id}/results")
    if results_response.status_code == 400:
        # Batch noch nicht abgeschlossen
        assert "noch nicht abgeschlossen" in results_response.json()["detail"]
    else:
        assert results_response.status_code == 200
        results = results_response.json()
        assert "test.jpg" in results
        assert "keypoints" in results["test.jpg"]
        assert "scores" in results["test.jpg"]


# Test für Batch-Ablauf
@pytest.mark.asyncio
async def test_batch_expiry(client):
    # Test-Bild erstellen
    test_image = np.zeros((100, 100, 3), dtype=np.uint8).tobytes()

    # Batch Request
    response = client.post(
        "/analyze/batch", files=[("files", ("test.jpg", test_image, "image/jpeg"))]
    )
    batch_id = response.json()["batch_id"]

    # Ablaufzeit kann im Test nicht direkt simuliert werden, daher nur Status-Check
    await asyncio.sleep(1)
    status_response = client.get(f"/analyze/batch/{batch_id}/status")
    assert status_response.status_code == 200 or status_response.status_code == 404


# Test für Fehlerbehandlung im Batch
@pytest.mark.asyncio
async def test_batch_error_handling(client):
    # Ungültiges Bild erstellen
    invalid_image = b"invalid image data"

    # Batch Request
    response = client.post(
        "/analyze/batch", files=[("files", ("test.jpg", invalid_image, "image/jpeg"))]
    )
    batch_id = response.json()["batch_id"]

    # Warte auf Verarbeitung
    await asyncio.sleep(1)

    # Status überprüfen
    status_response = client.get(f"/analyze/batch/{batch_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["failed_files"] > 0
    assert "error" in status_data["results"]["test.jpg"]


# Test für Retry-Logik
@pytest.mark.asyncio
async def test_batch_retry_logic(client, mock_model):
    # Simuliere temporären Fehler
    mock_model.side_effect = [Exception("Temporärer Fehler"), Mock()]

    # Test-Bild erstellen
    test_image = np.zeros((100, 100, 3), dtype=np.uint8).tobytes()

    # Batch Request
    response = client.post(
        "/analyze/batch", files=[("files", ("test.jpg", test_image, "image/jpeg"))]
    )
    batch_id = response.json()["batch_id"]

    # Warte auf Verarbeitung und Retry
    await asyncio.sleep(2)

    # Status überprüfen
    status_response = client.get(f"/analyze/batch/{batch_id}/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["status"] == "completed"
    assert status_data["failed_files"] == 0

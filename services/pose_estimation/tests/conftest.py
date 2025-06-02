import pytest
import pytest_asyncio
import redis.asyncio as redis
import os
import sys
from unittest.mock import Mock, patch
import numpy as np
import torch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import importlib
import config
import main
import time
from typing import Optional
import cv2

# Test-Umgebung konfigurieren
os.environ["TESTING"] = "1"
os.environ["MODEL_TYPE"] = "cpu"
os.environ["MAX_WORKERS"] = "2"
os.environ["MEMORY_LIMIT"] = "1024"
os.environ["BATCH_SIZE_LIMIT"] = "100"
os.environ["PROCESSING_TIMEOUT"] = "300"
importlib.reload(config)
from main import force_reload_settings
force_reload_settings()
importlib.reload(main)
from main import app

# Test Client Fixture
def client():
    return TestClient(app)

# In-Memory-Redis für Tests
class InMemoryRedis:
    def __init__(self):
        self.store = {}
        self.expiry = {}

    async def get(self, key: str) -> Optional[str]:
        if key in self.store:
            if key in self.expiry and self.expiry[key] < time.time():
                del self.store[key]
                del self.expiry[key]
                return None
            return self.store[key]
        return None

    async def setex(self, key: str, ttl: int, value: str):
        self.store[key] = value
        self.expiry[key] = time.time() + ttl

    async def flushdb(self):
        self.store.clear()
        self.expiry.clear()

    async def close(self):
        self.store.clear()
        self.expiry.clear()

# Redis Fixture
@pytest.fixture
async def redis_client():
    client = InMemoryRedis()
    yield client
    await client.close()

# Mock für das Pose Estimation Modell
@pytest.fixture
def mock_model():
    with patch("main.init_model") as mock:
        model = Mock()
        # Mock für die Modell-Ausgabe
        mock_keypoints = [[[100, 200], [150, 250], [200, 300]]]
        mock_scores = [[0.9, 0.8, 0.7]]
        model.return_value = Mock(
            pred_instances=Mock(get=Mock(return_value=mock_keypoints))
        )
        yield mock

# Test-Bild Fixture
@pytest.fixture
def test_image():
    return np.zeros((100, 100, 3), dtype=np.uint8).tobytes()

# Batch Test-Bilder Fixture
@pytest.fixture
def test_batch_images():
    return [np.zeros((100, 100, 3), dtype=np.uint8).tobytes() for _ in range(3)]

# Temporäres Verzeichnis Fixture
@pytest.fixture
def temp_dir(tmp_path):
    return str(tmp_path)

# Mock für Redis-Verbindungsfehler
@pytest.fixture
def mock_redis_error():
    with patch("redis.asyncio.Redis") as mock:
        mock.return_value.ping.side_effect = redis.ConnectionError
        yield mock

# Mock für Modell-Initialisierungsfehler
@pytest.fixture
def mock_model_init_error():
    with patch("main.init_model") as mock:
        mock.side_effect = Exception("Modell-Initialisierungsfehler")
        yield mock

# System Metrics Mock
@pytest.fixture
def mock_system_metrics():
    with patch("main.get_system_metrics") as mock:
        mock.return_value = {
            "cpu_usage": 50.0,
            "memory_usage": 512.0,
            "processing_queue": 2,
        }
        yield mock

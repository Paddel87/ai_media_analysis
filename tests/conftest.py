"""
Zentrale Test-Konfiguration mit gemeinsamen Fixtures und Utilities.
"""

import os
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, Generator
import requests
from fastapi.testclient import TestClient

# Test-Umgebungs-Konfiguration
os.environ["TESTING"] = "true"
os.environ["LOG_LEVEL"] = "WARNING"

@pytest.fixture(scope="session")
def event_loop():
    """Session-wide event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Standard Test-Konfiguration für alle Services."""
    return {
        "testing": True,
        "log_level": "WARNING",
        "redis_url": "redis://localhost:6379/1",
        "vector_db_url": "http://localhost:8001",
        "api_host": "localhost",
        "api_port": 8000,
        "gpu_enabled": False,
        "batch_size": 2,
        "max_workers": 2,
        "timeout": 30,
        "secret_key": "test-secret-key-for-testing-only",
        "openai_api_key": "test-openai-key",
        "model_cache_dir": "/tmp/test_models"
    }

@pytest.fixture
def mock_redis():
    """Mock Redis Client für Tests."""
    mock = Mock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    mock.exists.return_value = False
    mock.ping.return_value = True
    return mock

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI Client für Tests."""
    mock = Mock()
    mock.embeddings.create.return_value = Mock(
        data=[Mock(embedding=[0.1, 0.2, 0.3] * 512)]
    )
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )
    return mock

@pytest.fixture
def mock_torch_model():
    """Mock PyTorch Model für Tests."""
    mock = Mock()
    mock.eval.return_value = mock
    mock.to.return_value = mock
    mock.forward.return_value = Mock(
        logits=Mock(shape=(1, 2)),
        detach=Mock(return_value=Mock(cpu=Mock(return_value=Mock(numpy=Mock(return_value=[[0.8, 0.2]])))))
    )
    return mock

@pytest.fixture
def sample_image_data():
    """Sample image data für Vision Pipeline Tests."""
    import numpy as np
    return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

@pytest.fixture
def sample_audio_data():
    """Sample audio data für Whisper Tests."""
    import numpy as np
    return np.random.randn(16000).astype(np.float32)  # 1 second at 16kHz

@pytest.fixture
def sample_text_data():
    """Sample text data für LLM Tests."""
    return [
        "Dies ist ein Testtext für die Analyse.",
        "Another test sentence in English.",
        "Ein weiterer deutscher Testtext."
    ]

@pytest.fixture
def mock_http_client():
    """Mock HTTP Client für Service-Kommunikation."""
    mock = Mock()
    mock.get.return_value = Mock(
        status_code=200,
        json=Mock(return_value={"status": "ok"}),
        text="OK"
    )
    mock.post.return_value = Mock(
        status_code=200,
        json=Mock(return_value={"result": "success"}),
        text="Success"
    )
    return mock

@pytest.fixture
def test_files_dir():
    """Verzeichnis mit Test-Dateien."""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def docker_compose_override():
    """Docker Compose Override für Tests."""
    return {
        "version": "3.8",
        "services": {
            "redis": {
                "ports": ["6380:6379"]  # Anderer Port für Tests
            },
            "vector-db": {
                "environment": ["TESTING=true"]
            }
        }
    }

# Health Check Helpers
def wait_for_service(url: str, timeout: int = 30) -> bool:
    """Wartet bis Service verfügbar ist."""
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False

# Test Data Generators
def generate_test_embeddings(count: int = 10, dim: int = 512):
    """Generiert Test-Embeddings."""
    import numpy as np
    return np.random.randn(count, dim).astype(np.float32)

def generate_test_images(count: int = 5, width: int = 224, height: int = 224):
    """Generiert Test-Bilder."""
    import numpy as np
    return [np.random.randint(0, 255, (height, width, 3), dtype=np.uint8) for _ in range(count)]

# Custom Pytest Markers
def pytest_configure(config):
    """Registriert Custom Markers."""
    config.addinivalue_line("markers", "requires_gpu: Test benötigt GPU")
    config.addinivalue_line("markers", "requires_models: Test benötigt ML-Modelle")
    config.addinivalue_line("markers", "requires_internet: Test benötigt Internet-Verbindung")

def pytest_collection_modifyitems(config, items):
    """Modifiziert Test-Collection basierend auf Umgebung."""
    skip_gpu = pytest.mark.skip(reason="GPU nicht verfügbar")
    skip_models = pytest.mark.skip(reason="ML-Modelle nicht verfügbar")
    skip_internet = pytest.mark.skip(reason="Keine Internet-Verbindung")
    
    for item in items:
        if "requires_gpu" in item.keywords and not os.environ.get("GPU_AVAILABLE"):
            item.add_marker(skip_gpu)
        if "requires_models" in item.keywords and not os.environ.get("MODELS_AVAILABLE"):
            item.add_marker(skip_models)
        if "requires_internet" in item.keywords and not os.environ.get("INTERNET_AVAILABLE"):
            item.add_marker(skip_internet) 
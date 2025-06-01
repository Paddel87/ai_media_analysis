import pytest
import os
import sys
from pathlib import Path

# Projekt-Root zum Python-Pfad hinzufügen
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)


# Test-Konfiguration
def pytest_configure(config):
    """
    Konfiguriert die Test-Umgebung
    """
    # Marker registrieren
    config.addinivalue_line("markers", "integration: markiert Integrationstests")
    config.addinivalue_line("markers", "performance: markiert Performance-Tests")


# Fixtures
@pytest.fixture(autouse=True)
def setup_test_env():
    """
    Setzt die Test-Umgebung auf
    """
    # Test-Umgebungsvariablen setzen
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["GOOGLE_API_KEY"] = "test-key"
    os.environ["VECTOR_DB_URL"] = "http://vector-db:8000"
    os.environ["MEDIA_SERVICE_URL"] = "http://media-service:8000"
    os.environ["ANALYTICS_SERVICE_URL"] = "http://analytics-service:8000"
    os.environ["CACHE_SERVICE_URL"] = "http://cache-service:8000"
    os.environ["MONITORING_SERVICE_URL"] = "http://monitoring-service:8000"

    yield

    # Aufräumen
    for key in [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "VECTOR_DB_URL",
        "MEDIA_SERVICE_URL",
        "ANALYTICS_SERVICE_URL",
        "CACHE_SERVICE_URL",
        "MONITORING_SERVICE_URL",
    ]:
        os.environ.pop(key, None)


@pytest.fixture
def mock_requests():
    """
    Mock für HTTP-Requests
    """
    import requests
    from unittest.mock import patch

    with patch("requests.get") as mock_get, patch("requests.post") as mock_post, patch(
        "requests.delete"
    ) as mock_delete:
        yield {"get": mock_get, "post": mock_post, "delete": mock_delete}


@pytest.fixture
def mock_services():
    """
    Mock für externe Services
    """
    from unittest.mock import Mock

    return {
        "vector_db": Mock(),
        "media": Mock(),
        "analytics": Mock(),
        "cache": Mock(),
        "monitoring": Mock(),
    }

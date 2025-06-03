# AI Media Analysis System - Feature Testing Regelwerk
# Version: 1.0.0
# Status: Aktiv - OBLIGATORISCH für alle neuen Features

## Testing-Philosophie
- **Test-First Development**: Tests vor der Feature-Implementierung schreiben
- **Comprehensive Coverage**: Unit-, Integration- und E2E-Tests für jedes Feature
- **Automated Verification**: Alle Tests müssen in der CI/CD Pipeline laufen
- **Documentation Testing**: Tests müssen dokumentiert und maintainable sein
- **Quality Gates**: Kein Feature ohne erfolgreiche Tests deploybar

## Obligatorische Test-Requirements

### 1. Unit Tests (PFLICHT)
- **Coverage**: Minimum 80% Code Coverage für neue Features
- **Framework**: pytest mit fixtures und parametrized tests
- **Isolation**: Jeder Test muss unabhängig und isoliert laufen
- **Naming**: Klare, beschreibende Test-Namen

```python
# ✅ Korrekt - Beispiel Unit Test
def test_video_processing_extracts_frames_correctly():
    """Test that video processing extracts the correct number of frames."""
    # Given
    mock_video = create_mock_video(duration=10, fps=30)
    processor = VideoProcessor(frame_interval=1.0)

    # When
    frames = processor.extract_frames(mock_video)

    # Then
    assert len(frames) == 10
    assert all(frame.shape == (720, 1280, 3) for frame in frames)

def test_video_processing_handles_invalid_input():
    """Test that video processing raises appropriate error for invalid input."""
    processor = VideoProcessor()

    with pytest.raises(VideoProcessingError, match="Invalid video format"):
        processor.extract_frames(None)
```

### 2. Integration Tests (PFLICHT)
- **Service Integration**: Tests zwischen Services
- **Database Integration**: Tests mit echter Datenbank
- **API Integration**: Tests der HTTP-Endpoints
- **Docker Integration**: Tests mit Docker-Containern

```python
# ✅ Korrekt - Beispiel Integration Test
@pytest.mark.integration
async def test_llm_service_processes_video_analysis_request():
    """Test LLM service integration with video analysis pipeline."""
    # Given
    async with AsyncClient(app=app, base_url="http://test") as client:
        video_data = await create_test_video()

        # When
        response = await client.post(
            "/analyze/video",
            files={"video": video_data},
            data={"analysis_type": "content_detection"}
        )

        # Then
        assert response.status_code == 200
        result = response.json()
        assert "analysis_id" in result
        assert "status" in result
        assert result["status"] == "processing"
```

### 3. Feature Tests (PFLICHT)
- **End-to-End**: Vollständige Feature-Workflows
- **User Journey**: Realistische Benutzerszenarien
- **Performance**: Lasttest für neue Features
- **Security**: Sicherheitstests für neue Endpoints

```python
# ✅ Korrekt - Beispiel Feature Test
@pytest.mark.e2e
@pytest.mark.slow
async def test_complete_video_analysis_workflow():
    """Test complete video analysis from upload to result retrieval."""
    # Given
    test_video = await upload_test_video()

    # When - Upload video
    upload_response = await client.post("/upload", files={"video": test_video})
    video_id = upload_response.json()["video_id"]

    # When - Start analysis
    analysis_response = await client.post(f"/analyze/{video_id}")
    analysis_id = analysis_response.json()["analysis_id"]

    # When - Wait for completion (with timeout)
    result = await wait_for_analysis_completion(analysis_id, timeout=300)

    # Then
    assert result["status"] == "completed"
    assert "objects_detected" in result
    assert "faces_detected" in result
    assert len(result["objects_detected"]) > 0
```

## Test-Organisation

### Verzeichnisstruktur
```
tests/
├── unit/                    # Unit Tests
│   ├── services/
│   │   ├── test_llm_service.py
│   │   ├── test_video_processor.py
│   │   └── ...
│   └── utils/
├── integration/             # Integration Tests
│   ├── test_service_communication.py
│   ├── test_database_operations.py
│   └── test_api_endpoints.py
├── e2e/                    # End-to-End Tests
│   ├── test_video_analysis_workflow.py
│   ├── test_user_management.py
│   └── ...
├── performance/            # Performance Tests
│   ├── test_load_testing.py
│   └── test_stress_testing.py
├── fixtures/               # Test Fixtures
│   ├── conftest.py
│   ├── video_fixtures.py
│   └── data_fixtures.py
└── utils/                  # Test Utilities
    ├── mock_services.py
    ├── test_helpers.py
    └── ...
```

### Test-Konfiguration (pytest.ini)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=services
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
    performance: Performance tests
    smoke: Smoke tests
```

## CI/CD Integration

### GitHub Actions Testing Workflow
```yaml
# .github/workflows/feature-testing.yml
name: Feature Testing
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-ci.txt
      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=services --cov-fail-under=80

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-ci.txt
      - name: Run integration tests
        run: |
          pytest tests/integration/ -v
        env:
          REDIS_URL: redis://localhost:6379
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests]
    steps:
      - uses: actions/checkout@v4
      - name: Start services with Docker Compose
        run: |
          docker-compose up -d
          sleep 30  # Wait for services to start
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-ci.txt
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --maxfail=1
      - name: Stop services
        run: docker-compose down
```

## Test Data Management

### Test Fixtures
```python
# tests/fixtures/conftest.py
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from services.main import app

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client for API testing."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_video_data():
    """Sample video data for testing."""
    return {
        "filename": "test_video.mp4",
        "duration": 120,
        "fps": 30,
        "resolution": "1920x1080"
    }

@pytest.fixture
async def mock_llm_service():
    """Mock LLM service for testing."""
    from unittest.mock import AsyncMock
    mock_service = AsyncMock()
    mock_service.analyze.return_value = {
        "analysis_id": "test-123",
        "status": "completed",
        "results": {"objects": ["person", "car"]}
    }
    return mock_service
```

### Test Data Files
```
tests/data/
├── videos/
│   ├── test_video_short.mp4     # 10 sec test video
│   ├── test_video_medium.mp4    # 1 min test video
│   └── test_video_corrupted.mp4 # Corrupted for error testing
├── images/
│   ├── test_image.jpg
│   └── test_image_nsfw.jpg
└── json/
    ├── expected_results.json
    └── mock_responses.json
```

## Performance Testing

### Load Testing (Locust)
```python
# tests/performance/test_load_testing.py
from locust import HttpUser, task, between

class VideoAnalysisUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Setup user session."""
        self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_pass"
        })

    @task(3)
    def upload_video(self):
        """Test video upload under load."""
        with open("tests/data/videos/test_video_short.mp4", "rb") as f:
            self.client.post("/upload", files={"video": f})

    @task(1)
    def check_analysis_status(self):
        """Test analysis status checking."""
        self.client.get("/analysis/status/test-id")
```

### Memory and Performance Tests
```python
# tests/performance/test_memory_usage.py
import psutil
import pytest
from memory_profiler import profile

@pytest.mark.performance
@profile
def test_video_processing_memory_usage():
    """Test memory usage during video processing."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss

    # Process large video
    processor = VideoProcessor()
    processor.process_large_video("tests/data/videos/large_video.mp4")

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Memory increase should be less than 500MB
    assert memory_increase < 500 * 1024 * 1024
```

## Test Documentation

### Test-spezifische README
```markdown
# tests/README.md

## Test-Ausführung

### Alle Tests
```bash
make test
```

### Spezifische Test-Kategorien
```bash
# Unit Tests
pytest tests/unit/ -v

# Integration Tests
pytest tests/integration/ -v

# E2E Tests
pytest tests/e2e/ -v

# Performance Tests
pytest tests/performance/ -v
```

### Coverage Reports
```bash
# HTML Coverage Report
pytest --cov=services --cov-report=html
open htmlcov/index.html
```
```

## Makefile Integration

### Test-Targets im Makefile
```makefile
# Makefile Test-Targets
.PHONY: test test-unit test-integration test-e2e test-performance test-coverage

test: test-unit test-integration test-e2e
	@echo "✅ Alle Tests erfolgreich!"

test-unit:
	@echo "🧪 Führe Unit Tests aus..."
	pytest tests/unit/ -v --cov=services --cov-fail-under=80

test-integration:
	@echo "🔗 Führe Integration Tests aus..."
	pytest tests/integration/ -v

test-e2e:
	@echo "🎯 Führe E2E Tests aus..."
	docker-compose up -d
	sleep 30
	pytest tests/e2e/ -v --maxfail=1
	docker-compose down

test-performance:
	@echo "⚡ Führe Performance Tests aus..."
	pytest tests/performance/ -v

test-coverage:
	@echo "📊 Generiere Coverage Report..."
	pytest --cov=services --cov-report=html --cov-report=term-missing
	@echo "Coverage Report: htmlcov/index.html"
```

## Qualitätskontrolle

### Definition of Done für Features
- [ ] Unit Tests geschrieben (min. 80% Coverage)
- [ ] Integration Tests implementiert
- [ ] E2E Test für Hauptworkflow erstellt
- [ ] Performance Test bei relevanten Features
- [ ] Alle Tests laufen erfolgreich in CI/CD
- [ ] Test-Dokumentation aktualisiert
- [ ] Code Review mit Fokus auf Tests durchgeführt

### Test Review Checklist
- [ ] Tests testen das richtige Verhalten
- [ ] Tests sind unabhängig und isoliert
- [ ] Test-Namen sind beschreibend
- [ ] Edge Cases werden abgedeckt
- [ ] Error Cases werden getestet
- [ ] Performance-kritische Pfade sind getestet
- [ ] Mocks und Fixtures sind sinnvoll eingesetzt

## Monitoring und Maintenance

### Test-Metriken
- **Test Coverage**: Minimum 80% für neue Features
- **Test Execution Time**: Unit Tests < 30s, Integration < 5min
- **Test Success Rate**: > 95% in CI/CD Pipeline
- **Test Maintenance**: Broken Tests müssen innerhalb 24h gefixt werden

### Automatische Test-Updates
```python
# scripts/update_test_fixtures.py
"""Script to update test fixtures automatically."""
def update_test_data():
    """Update test data from production anonymized samples."""
    # Implementation for updating test fixtures
    pass

if __name__ == "__main__":
    update_test_data()
```

## Integration mit anderen Regeln

### Verbindung zu Iterative Development
- Tests folgen dem 4-Iterations-Modell
- Iteration 1: Basis-Unit-Tests
- Iteration 2: Integration Tests
- Iteration 3: E2E Tests
- Iteration 4: Performance Tests

### Verbindung zu Formatierung
- Alle Test-Dateien müssen Black/isort konform sein
- Test-Code unterliegt denselben Qualitätsstandards
- Docstrings in Tests sind obligatorisch

### Verbindung zu Dokumentation
- Tests müssen in der API-Dokumentation referenziert werden
- Test-Coverage wird in STATUS.md getrackt
- Test-Strategien werden in CONTRIBUTING.md dokumentiert

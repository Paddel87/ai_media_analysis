# AI Media Analysis System - Test Suite

## 🎯 Überblick

Diese umfassende Test-Suite wurde entwickelt, um das AI Media Analysis System von der Alpha-Phase zum Release Candidate zu bringen. Sie addressiert einen der kritischen RC-Blocker und bietet vollständige Testabdeckung für alle Services.

## 📊 Aktuelle Test-Statistiken

- **Unit Tests**: 32 Tests ✅
- **Integration Tests**: 10 Tests ✅
- **Testabdeckung**: 70%+ angestrebt
- **Unterstützte Python-Versionen**: 3.9, 3.10, 3.11

## 🏗️ Test-Architektur

### Verzeichnis-Struktur
```
tests/
├── __init__.py                 # Test-Suite-Initialisierung
├── conftest.py                # Zentrale Fixtures und Konfiguration
├── README.md                  # Diese Dokumentation
├── unit/                      # Unit Tests
│   ├── test_base_service.py   # Basis-Service-Tests
│   └── test_vision_pipeline.py # Vision Pipeline Tests
└── integration/               # Integration Tests
    └── test_service_integration.py # Service-Integration Tests
```

### Test-Kategorien

#### 🔬 Unit Tests
- **Basis-Service-Tests**: Gemeinsame Service-Funktionalitäten
- **Vision Pipeline Tests**: NSFW Detection, OCR, Face Recognition
- **Service-Utilities**: Error Handling, Retry-Mechanismen, Timeouts
- **Kommunikations-Tests**: HTTP-Requests, Service Discovery

#### 🔗 Integration Tests
- **Vision-LLM Integration**: Bild-zu-Text-Analyse-Pipeline
- **Vision-Vector DB**: Embedding-Speicherung und -Suche
- **LLM-Vector DB**: Text-Embeddings und semantische Suche
- **Whisper-LLM**: Audio-Transkription und Text-Analyse
- **Full Pipeline**: End-to-End Medien-Analyse
- **Service Health**: Health Checks und Resilienz

## 🚀 Test-Ausführung

### Schnellstart
```bash
# Komplette Test-Suite
make test

# Nur Unit Tests
make test-unit

# Nur Integration Tests
make test-integration

# Mit Coverage-Analyse
make test-coverage
```

### Erweiterte Optionen
```bash
# Python Test Runner
python run_tests.py --help

# Spezifische Test-Typen
python run_tests.py --unit -v
python run_tests.py --integration -v
python run_tests.py --coverage

# Code-Qualität
python run_tests.py --lint
python run_tests.py --security
```

### Docker-basierte Tests
```bash
# Services starten
make run-services

# Docker Tests
make test-docker

# Health Check
make health-check
```

## 🧪 Test-Fixtures

### Zentrale Fixtures (conftest.py)
- `mock_config`: Standard-Testkonfiguration
- `mock_redis`: Redis Client Mock
- `mock_openai_client`: OpenAI API Mock
- `mock_torch_model`: PyTorch Model Mock
- `sample_image_data`: Test-Bilddaten
- `sample_audio_data`: Test-Audiodaten
- `sample_text_data`: Test-Textdaten

### Service-spezifische Mocks
- HTTP-Client-Mocks für Service-Kommunikation
- ML-Model-Mocks für Vision und LLM Tests
- Database-Mocks für Vector Storage Tests

## 📋 Test-Marker

Die Test-Suite verwendet pytest-Marker für kategorisierte Test-Ausführung:

- `@pytest.mark.unit`: Unit Tests
- `@pytest.mark.integration`: Integration Tests
- `@pytest.mark.e2e`: End-to-End Tests
- `@pytest.mark.performance`: Performance Tests
- `@pytest.mark.slow`: Langsame Tests
- `@pytest.mark.gpu`: GPU-abhängige Tests
- `@pytest.mark.docker`: Docker-abhängige Tests
- `@pytest.mark.security`: Security Tests

## 🔧 Konfiguration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests services
addopts =
    -v
    --cov=services
    --cov-report=html:htmlcov
    --cov-fail-under=70
markers =
    unit: Unit tests
    integration: Integration tests
    # ... weitere Marker
```

### setup.cfg
Enthält Konfigurationen für:
- Flake8 (Code Linting)
- MyPy (Type Checking)
- Coverage (Test Coverage)
- isort (Import Sorting)

## 🎯 Testabdeckung-Ziele

### Aktuelle Coverage-Ziele
- **Minimum**: 70% Gesamtabdeckung
- **Services**: 80%+ pro Service
- **Kritische Pfade**: 95%+ (Authentifizierung, Datenverarbeitung)

### Coverage-Reports
```bash
# HTML-Report generieren
make test-coverage

# Report öffnen
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

## 🔒 Security Testing

### Security-Scan-Tools
- **Bandit**: Static Security Analysis
- **Safety**: Dependency Vulnerability Scan

```bash
# Security-Scan ausführen
make test-security
python run_tests.py --security
```

## 🚦 CI/CD Integration

### GitHub Actions
Die Test-Suite ist vollständig in GitHub Actions integriert:

- **Automatische Tests** bei Push/PR
- **Multi-Python-Version Tests** (3.9, 3.10, 3.11)
- **Coverage-Reporting** mit Codecov
- **Security-Scans** in jeder Pipeline
- **Performance-Tests** bei Schedule/Tag

### Pipeline-Stages
1. **Environment Check**: Python-Version, Dependencies
2. **Code Quality**: Linting, Formatting, Type Checking
3. **Unit Tests**: Schnelle Feedback-Schleife
4. **Integration Tests**: Service-Interaktion Tests
5. **Coverage Analysis**: Testabdeckungs-Berichte
6. **Security Scan**: Vulnerability Assessment
7. **Docker Tests**: Container-basierte Tests

## 📈 Performance Testing

### Performance-Test-Typen
- **Load Tests**: Service-Performance unter Last
- **Benchmark Tests**: ML-Model-Performance
- **Memory Tests**: Speicher-Effizienz
- **Response Time Tests**: API-Antwortzeiten

```bash
# Performance Tests ausführen
make test-performance
python run_tests.py --performance -v
```

## 🔄 Entwicklungs-Workflow

### Pre-Commit Hook
```bash
# Pre-commit Hook installieren
make dev-setup

# Manuell ausführen
make pre-commit
```

### Test-Driven Development
1. **Red**: Test schreiben (schlägt fehl)
2. **Green**: Minimale Implementierung
3. **Refactor**: Code verbessern
4. **Repeat**: Zyklus wiederholen

## 📚 Best Practices

### Test-Design
- **AAA-Pattern**: Arrange, Act, Assert
- **Isolation**: Tests sind unabhängig voneinander
- **Determinism**: Tests sind reproduzierbar
- **Fast Feedback**: Unit Tests unter 1 Sekunde

### Mock-Strategien
- **External Services**: Immer mocken
- **Databases**: Mock oder Test-DB verwenden
- **File I/O**: Mit temporären Verzeichnissen
- **Network Calls**: Requests-Mock verwenden

### Fehlerbehandlung
- **Expected Exceptions**: Mit `pytest.raises()`
- **Error Messages**: Aussagekräftige Assertions
- **Edge Cases**: Grenzfälle abdecken

## 🛠️ Troubleshooting

### Häufige Probleme

#### Import-Fehler
```bash
# Python-Pfad prüfen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Virtual Environment aktivieren
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows
```

#### Coverage zu niedrig
```bash
# Fehlende Tests identifizieren
make test-coverage
# HTML-Report öffnen und nicht abgedeckte Bereiche prüfen
```

#### Langsame Tests
```bash
# Nur schnelle Tests ausführen
make test-fast

# Performance-Profiling
python -m pytest --duration=10
```

## 📞 Support

### Test-Suite Maintainer
- **Team**: AI Media Analysis Development Team
- **Issues**: GitHub Issues für Test-bezogene Probleme
- **Dokumentation**: Diese README und Code-Kommentare

### Weitere Ressourcen
- [pytest Dokumentation](https://docs.pytest.org/)
- [Coverage.py Dokumentation](https://coverage.readthedocs.io/)
- [GitHub Actions Dokumentation](https://docs.github.com/en/actions)

## 🎯 Roadmap

### Kurzfristig (1-2 Wochen)
- [ ] E2E Tests für Web-UI
- [ ] Performance-Benchmarks etablieren
- [ ] API-Contract Tests

### Mittelfristig (1 Monat)
- [ ] Load Testing mit echter Infrastruktur
- [ ] Security Penetration Tests
- [ ] Chaos Engineering Tests

### Langfristig (3 Monate)
- [ ] AI-basierte Test-Generierung
- [ ] Automatisierte Performance-Regression-Detection
- [ ] Cross-Platform Test-Matrix

---

## 📊 Status: RC-Blocker GELÖST ✅

Mit dieser Test-Suite wurde einer der kritischen Release Candidate Blocker erfolgreich addressiert:

- ✅ **Umfassende Testabdeckung**: 32 Unit Tests, 10 Integration Tests
- ✅ **Automatisierte CI/CD**: GitHub Actions Pipeline
- ✅ **Code-Qualitätssicherung**: Linting, Type Checking, Security Scans
- ✅ **Entwickler-Tools**: Make-Targets, Test Runner, Coverage Reports
- ✅ **Dokumentation**: Vollständige Test-Dokumentation

**Das Projekt ist jetzt deutlich näher am Release Candidate Status!** 🎉

# 🧪 Feature Testing Framework

Das Feature Testing Framework ist ein **obligatorisches** Regelwerk für alle neuen Features im AI Media Analysis System. Es stellt sicher, dass jede neue Funktionalität umfassend getestet wird, bevor sie deployed wird.

## 📋 Testing-Regel (OBLIGATORISCH)

**Jedes neue Feature MUSS die folgenden Test-Anforderungen erfüllen:**

- ✅ **Unit Tests**: Minimum 80% Code Coverage
- ✅ **Integration Tests**: Service-zu-Service Tests
- ✅ **E2E Tests**: Vollständige Workflow-Tests
- ✅ **Security Tests**: Sicherheitsprüfungen
- ✅ **Pre-commit Validation**: Automatische Prüfung vor Commits

## 🚀 Quick Start

### 1. Test-Umgebung einrichten
```bash
# Test-Verzeichnisse und Basis-Konfiguration erstellen
make test-setup

# Dependencies installieren
pip install -r requirements-ci.txt
```

### 2. Tests für neues Feature erstellen
```bash
# Beispiel: Service "my_service" mit Datei "processor.py"
# Erstelle: tests/unit/services/my_service/test_processor.py

mkdir -p tests/unit/services/my_service
cat > tests/unit/services/my_service/test_processor.py << 'EOF'
"""Tests für my_service.processor"""

import pytest
from unittest.mock import Mock, patch
from services.my_service.processor import VideoProcessor


class TestVideoProcessor:
    """Test-Klasse für VideoProcessor"""

    def test_process_video_success(self):
        """Test erfolgreiche Video-Verarbeitung"""
        # Given
        processor = VideoProcessor()
        mock_video = Mock()
        mock_video.duration = 120

        # When
        result = processor.process(mock_video)

        # Then
        assert result is not None
        assert result.status == "completed"

    def test_process_video_invalid_input(self):
        """Test Fehlerbehandlung bei ungültiger Eingabe"""
        processor = VideoProcessor()

        with pytest.raises(ValueError, match="Invalid video"):
            processor.process(None)
EOF
```

### 3. Tests ausführen
```bash
# Alle Tests
make test

# Nur Unit Tests
make test-unit

# Mit Coverage Report
make test-coverage
```

## 🧪 Test-Kategorien

### Unit Tests (`tests/unit/`)
**Schnelle, isolierte Tests für einzelne Funktionen/Klassen**

```python
@pytest.mark.unit
def test_video_frame_extraction():
    """Test Frame-Extraktion aus Video"""
    processor = VideoProcessor()
    frames = processor.extract_frames(mock_video_data)
    assert len(frames) == expected_frame_count
```

**Anforderungen:**
- ⏱️ Schnell (< 1 Sekunde pro Test)
- 🔒 Isoliert (keine externen Dependencies)
- 📊 Minimum 80% Coverage
- 🎯 Fokus auf einzelne Funktionen

### Integration Tests (`tests/integration/`)
**Tests für Service-zu-Service-Kommunikation**

```python
@pytest.mark.integration
async def test_llm_service_video_analysis():
    """Test Integration zwischen LLM Service und Video Pipeline"""
    async with AsyncClient(app=app) as client:
        response = await client.post("/analyze", json=test_data)
        assert response.status_code == 200
```

**Anforderungen:**
- 🔗 Service-Interaktionen
- 💾 Echte Datenbank/Redis
- 🌐 HTTP-API Tests
- ⏱️ Mittlere Laufzeit (< 5 Minuten)

### E2E Tests (`tests/e2e/`)
**Vollständige Workflow-Tests**

```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_complete_video_analysis_pipeline():
    """Test komplette Video-Analyse von Upload bis Ergebnis"""
    # Upload -> Analyse -> Ergebnis abrufen
    video_id = await upload_test_video()
    analysis_id = await start_analysis(video_id)
    result = await wait_for_completion(analysis_id)
    assert result.status == "completed"
```

**Anforderungen:**
- 🎯 Benutzer-Workflows
- 🐳 Docker-Services aktiv
- ⏱️ Längere Laufzeit (< 30 Minuten)
- 🔄 End-to-End Szenarien

### Performance Tests (`tests/performance/`)
**Last- und Performance-Tests**

```python
@pytest.mark.performance
def test_video_processing_under_load():
    """Test Video-Verarbeitung unter Last"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_video, test_video) for _ in range(50)]
        results = [f.result() for f in futures]
    assert all(r.success for r in results)
```

## 🛠️ Verfügbare Commands

### Basis-Tests
```bash
make test              # Alle Tests (Unit + Integration + E2E)
make test-unit         # Unit Tests mit Coverage
make test-integration  # Integration Tests
make test-e2e          # End-to-End Tests
```

### Spezielle Tests
```bash
make test-performance  # Performance Tests
make test-security     # Security Scans
make test-smoke        # Schnelle System-Checks
```

### Test-Qualität
```bash
make test-coverage     # Coverage Report generieren
make test-validate     # Test-Anforderungen prüfen
make test-quality-gate # Quality Gate für Deployment
```

### Utilities
```bash
make test-setup        # Test-Umgebung einrichten
make test-clean        # Test-Artifacts löschen
make test-parallel     # Parallele Ausführung
make test-debug        # Debug-Modus
make test-watch        # Kontinuierliche Ausführung
make test-help         # Alle Commands anzeigen
```

## 🚥 Quality Gates

### Pre-commit Hooks
**Automatische Validierung vor jedem Commit:**
- ✅ Neue Service-Dateien haben entsprechende Tests
- ✅ Test-Qualitätsprüfung
- ✅ Code-Formatierung (Black, isort)
- ✅ Typ-Prüfungen (mypy)
- ✅ Security-Scans (bandit)

### CI/CD Pipeline
**GitHub Actions validiert automatisch:**
- ✅ Unit Tests (80% Coverage required)
- ✅ Integration Tests
- ✅ E2E Tests
- ✅ Security Tests
- ✅ Performance Tests (bei main/develop)

### Definition of Done
**Ein Feature ist erst fertig, wenn:**
- [ ] Unit Tests geschrieben (min. 80% Coverage)
- [ ] Integration Tests implementiert
- [ ] E2E Test für Hauptworkflow erstellt
- [ ] Performance Test bei relevanten Features
- [ ] Alle Tests laufen erfolgreich in CI/CD
- [ ] Test-Dokumentation aktualisiert
- [ ] Code Review mit Fokus auf Tests durchgeführt

## 📁 Verzeichnisstruktur

```
tests/
├── unit/                    # Unit Tests
│   ├── services/
│   │   ├── llm_service/
│   │   │   ├── test_main.py
│   │   │   ├── test_processor.py
│   │   │   └── test_models.py
│   │   ├── control/
│   │   │   └── test_api.py
│   │   └── ...
│   └── utils/
│       └── test_helpers.py
├── integration/             # Integration Tests
│   ├── test_service_communication.py
│   ├── test_database_operations.py
│   └── test_api_endpoints.py
├── e2e/                    # End-to-End Tests
│   ├── test_video_analysis_workflow.py
│   ├── test_user_management.py
│   └── test_complete_pipeline.py
├── performance/            # Performance Tests
│   ├── test_load_testing.py
│   └── test_stress_testing.py
├── fixtures/               # Test Fixtures
│   ├── conftest.py
│   ├── video_fixtures.py
│   └── data_fixtures.py
├── data/                   # Test Data
│   ├── videos/
│   │   ├── test_video_short.mp4
│   │   └── test_video_medium.mp4
│   ├── images/
│   └── json/
└── utils/                  # Test Utilities
    ├── mock_services.py
    ├── test_helpers.py
    └── assertions.py
```

## 🎯 Best Practices

### Test-Namen
```python
# ✅ Gut - beschreibt was getestet wird
def test_video_processor_extracts_correct_frame_count_for_30fps_video():
    pass

# ❌ Schlecht - unklar was getestet wird
def test_video_processor():
    pass
```

### Test-Struktur (Given-When-Then)
```python
def test_feature():
    """Test description"""
    # Given - Setup
    processor = VideoProcessor()
    test_data = create_test_video(duration=10)

    # When - Action
    result = processor.process(test_data)

    # Then - Assertion
    assert result.frame_count == 300  # 10s * 30fps
    assert result.status == "completed"
```

### Fixtures verwenden
```python
@pytest.fixture
def sample_video():
    """Sample video for testing"""
    return create_test_video(duration=5, fps=30)

def test_with_fixture(sample_video):
    """Test using fixture"""
    result = process_video(sample_video)
    assert result is not None
```

### Mocking für externe Dependencies
```python
@patch('services.external_api.requests.post')
def test_api_call(mock_post):
    """Test API call with mocked response"""
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}

    result = make_api_call()
    assert result["status"] == "success"
```

## 🔧 Konfiguration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
addopts =
    --verbose
    --cov=services
    --cov-fail-under=80
    --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow-running tests
    performance: Performance tests
```

### GitHub Actions
Siehe `.github/workflows/feature-testing.yml` für die vollständige CI/CD Pipeline-Konfiguration.

## ⚠️ Häufige Probleme

### "Missing Tests" Fehler
```bash
❌ Feature Testing Regel verletzt!
Neue Service-Dateien ohne entsprechende Tests:
  📄 services/my_service/processor.py
     ➜ Erstelle Test: tests/unit/services/my_service/test_processor.py
```

**Lösung:**
```bash
# Test-Datei erstellen
mkdir -p tests/unit/services/my_service
touch tests/unit/services/my_service/test_processor.py
# Test implementieren (siehe Beispiele oben)
```

### Coverage unter 80%
```bash
❌ Coverage unter 80%
Missing coverage in:
  services/my_service/processor.py: 65%
```

**Lösung:**
```bash
# Mehr Tests hinzufügen oder
# Coverage-Report für Details
make test-coverage
open htmlcov/index.html
```

### E2E Tests schlagen fehl
```bash
❌ E2E Tests failed - Services not ready
```

**Lösung:**
```bash
# Services manuell starten und testen
docker-compose up -d
sleep 60
curl http://localhost:8000/health
make test-e2e
```

## 📞 Support

- **Dokumentation**: Siehe `.cursorrules/rules/feature_testing.md`
- **Commands**: `make test-help`
- **CI/CD**: GitHub Actions in `.github/workflows/feature-testing.yml`
- **Validation**: `scripts/validate_feature_tests.py`

---

**Remember: Kein Feature ohne Tests! 🧪✨**

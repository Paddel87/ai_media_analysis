# Beitragsrichtlinien - Enterprise Development Framework

## Übersicht

Willkommen zum AI Media Analysis Projekt! Wir haben ein **Enterprise-Grade Development Framework** mit **5 verbindlichen Hauptentwicklungsregeln** implementiert. Diese Richtlinien gewährleisten höchste Code-Qualität und professionelle Entwicklungsstandards.

## 🏗️ Enterprise Development Framework

### 5 Hauptentwicklungsregeln (VERBINDLICH)

1. **✅ Feature Testing Regel** - Umfassende Test-Pipeline
2. **✅ Black Standard Regel** - Automatische Code-Formatierung
3. **✅ Konfigurationsdatei-Validierung** - Config-Qualitätssicherung
4. **✅ Linter-Compliance-Regel** - 7-Tool-Qualitäts-Pipeline
5. **✅ venv-Entwicklungsumgebung-Regel** - Environment-Isolation

### 🎯 Entwicklungsumgebung Setup (VERPFLICHTEND)

#### 1. venv-Umgebung (Regel 5 - OBLIGATORISCH)
```bash
# venv erstellen und aktivieren (VERPFLICHTEND für alle Entwicklungsarbeiten)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Automatisches Enterprise-Setup
make venv-setup
```

#### 2. Umgebungsvalidierung
```bash
# venv-Gesundheitscheck
make venv-check         # Health-Score: 0-100 Punkte

# Compliance-Validierung
make check-compliance   # 7-Tool-Pipeline-Check
```

#### 3. IDE-Konfiguration
```bash
# Automatische VS Code/Cursor Settings
make venv-setup         # Erstellt .vscode/settings.json automatisch
# Python Interpreter: .venv/Scripts/python.exe (Windows) oder .venv/bin/python (Linux/macOS)
```

## 🧪 Testing Framework (Regel 1)

### Test-Anforderungen (VERBINDLICH)
```bash
# Vollständige Test-Pipeline
make test               # Alle Tests (ERFORDERLICH vor Commits)

# Spezifische Test-Types
make test-unit          # Unit Tests (80%+ Coverage ERFORDERLICH)
make test-integration   # Service-Integration Tests
make test-e2e          # End-to-End Workflows
make test-performance  # Load Tests
make test-security     # Security Scans

# Test-Validierung für neue Features
make test-validate     # Prüft Test-Anforderungen
make test-quality-gate # Quality Gate für Merges
```

### Test-Coverage-Standards
- **✅ Unit Tests:** Minimum 80% Coverage (VERPFLICHTEND)
- **✅ Integration Tests:** Alle Service-Interaktionen
- **✅ E2E Tests:** Kritische User-Workflows
- **✅ Performance Tests:** Load Testing unter realistischen Bedingungen
- **✅ Security Tests:** Vulnerability Scans und Dependency-Checks

## 🎨 Code-Qualität Framework (Regeln 2, 4)

### Automatische Formatierung (Regel 2 - VERBINDLICH)
```bash
# Code formatieren (ERFORDERLICH vor jedem Commit)
make format             # Black (88 Zeichen) + isort
make fix-all           # Format + Lint + Config Fix

# Format-Validierung
make check-format      # Nur prüfen ohne Änderungen
make format-check-strict # Strenger Check für CI/CD
```

### Linter-Compliance-Pipeline (Regel 4 - 7 Tools)
```bash
# Vollständige Compliance-Prüfung
make check-compliance

# 3-Level-Compliance-System:
make check-compliance-critical  # MINIMUM (CI/CD-Requirement)
make check-compliance          # RECOMMENDED (Development Standard)
make check-compliance-strict   # EXCELLENCE (Production Ready)

# Automatische Reparatur
make fix-compliance    # Automatische Problembehebung
make compliance-report # Detaillierter Compliance-Report
```

### 7-Tool-Qualitäts-Pipeline
1. **Black:** Code-Formatierung (88 Zeichen, verbindlich)
2. **isort:** Import-Sortierung (automatisch)
3. **flake8:** Style Guide Enforcement (PEP8+)
4. **mypy:** Static Type Checking
5. **bandit:** Security Vulnerability Detection
6. **safety:** Dependency Security Scanning
7. **config-validation:** Konfigurationsdatei-Konsistenz

## 🏗️ Konfigurationsdatei-Management (Regel 3)

### Config-Validierung (VERBINDLICH)
```bash
# Alle Konfigurationsdateien validieren
make validate-config

# Spezifische Config-Checks
make check-pytest-ini         # pytest.ini
make check-pyproject          # pyproject.toml
make check-docker-compose     # docker-compose.yml

# Automatische Reparatur
make fix-config              # Config-Duplikate und Syntax
make config-health-check     # Umfassende Config-Prüfung
```

## 📋 Contribution-Workflow (Enterprise-Standard)

### 1. Vorbereitung (VERPFLICHTEND)
```bash
# 1. Repository forken und klonen
git clone https://github.com/your-fork/ai_media_analysis.git
cd ai_media_analysis

# 2. venv aktivieren (OBLIGATORISCH)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 3. Enterprise-Setup
make venv-setup

# 4. Umgebung validieren
make venv-check         # Health-Score sollte >80 sein
make check-compliance   # Alle Tools sollten grün sein
```

### 2. Feature-Entwicklung
```bash
# 1. Feature-Branch erstellen
git checkout -b feature/amazing-feature

# 2. Test-Anforderungen validieren (Regel 1)
make test-validate      # Prüft Test-Coverage-Anforderungen

# 3. Entwicklung mit kontinuierlicher Qualitätsprüfung
make test-watch         # Kontinuierliche Tests
make format-with-venv   # Formatierung mit venv-Check

# 4. Vor jedem Commit
make fix-all           # Automatische Formatierung + Linting
make test-unit         # Unit Tests (80%+ Coverage)
make check-compliance  # Linter-Compliance
```

### 3. Pre-Merge Validation (Quality Gates)
```bash
# Vollständiger Quality Gate Check
make pre-merge-check    # Alle Regeln validieren

# Einzelne Quality Gates
make test-quality-gate  # Test-Framework-Compliance
make compliance-gate    # Linter-Compliance
make venv-gate         # Environment-Compliance
make config-gate       # Konfigurationsdatei-Compliance
```

### 4. Pull Request Standards
```bash
# Pre-PR Checklist ausführen
make pr-checklist      # Automatische PR-Vorbereitung

# CI/CD Pipeline simulieren
make test-ci           # Lokale CI/CD-Simulation
```

## 📝 Pull Request Checkliste (Enterprise)

### Verpflichtende Checks ✅
- [ ] **venv aktiviert:** `.venv\Scripts\activate` ausgeführt
- [ ] **venv-Health >80:** `make venv-check` erfolgreich
- [ ] **Unit Tests 80%+:** `make test-unit` erfolgreich
- [ ] **Integration Tests:** `make test-integration` erfolgreich
- [ ] **Linter-Compliance:** `make check-compliance` erfolgreich
- [ ] **Code-Formatierung:** `make format` ausgeführt
- [ ] **Config-Validierung:** `make validate-config` erfolgreich
- [ ] **Security Scans:** `make test-security` erfolgreich
- [ ] **Pre-Merge Gate:** `make pre-merge-check` erfolgreich

### Feature-Spezifische Checks
- [ ] **Feature Tests:** Tests für neue Funktionalität
- [ ] **Documentation:** Code-Dokumentation mit Docstrings
- [ ] **API-Docs:** API.md bei neuen Endpoints aktualisiert
- [ ] **CHANGELOG:** CHANGELOG.md aktualisiert
- [ ] **Breaking Changes:** Kompatibilität dokumentiert

## 💻 Development-Environment

### System-Anforderungen
- **Python:** 3.11+ (für venv-Regel)
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 11+
- **IDE:** VS Code/Cursor mit Python-Extension
- **RAM:** 8GB (16GB empfohlen)
- **Storage:** 50GB SSD

### Entwicklungstools (Automatisch installiert)
```bash
# Development-Tools installieren
make venv-install-dev   # Linter, Formatter, Testing-Tools
make venv-install-test  # Test-Framework
make venv-install-all   # Alle Dependencies
```

## 🔧 Debugging und Hilfe

### Hilfe-System
```bash
# Framework-Hilfe
make help               # Alle verfügbaren Befehle
make venv-help         # venv-Management
make test-help         # Testing Framework
make lint-help         # Code-Qualität
make compliance-help   # Compliance-System

# Diagnose-Tools
make venv-doctor       # venv-Probleme diagnostizieren
make test-debug        # Test-Debugging
make monitor           # Service-Monitoring
```

### Häufige Probleme

#### venv-Probleme
```bash
# venv neu erstellen
make venv-clean-rebuild

# Diagnose
make venv-doctor        # Detaillierte Problemanalyse
```

#### Compliance-Probleme
```bash
# Automatische Reparatur
make fix-compliance

# Spezifische Tool-Fixes
make fix-black         # Black-Formatierung
make fix-isort         # Import-Sortierung
make fix-config        # Config-Reparatur
```

#### Test-Probleme
```bash
# Test-Debugging
make test-debug        # Verbose Test-Output
make test-isolation    # Tests isoliert ausführen
```

## 📊 Code-Review Standards

### Review-Kriterien (Enterprise)
1. **✅ Compliance:** Alle 5 Entwicklungsregeln erfüllt
2. **✅ Funktionalität:** Feature funktioniert wie spezifiziert
3. **✅ Tests:** 80%+ Coverage, alle Test-Types
4. **✅ Code-Qualität:** 7-Tool-Pipeline erfolgreich
5. **✅ Security:** Security-Scans bestanden
6. **✅ Performance:** Performance-Tests unter Last
7. **✅ Documentation:** Vollständige Code-Dokumentation
8. **✅ Maintenance:** Wartbarkeit und Readability

### Automated Quality Gates
- **GitHub Actions:** Automatische CI/CD-Pipeline
- **Pre-commit Hooks:** Automatische Formatierung
- **Merge-Blocking:** Kritische Failures verhindern Merges
- **Quality Reports:** Automatische Code-Quality-Reports

## 🎯 Commit-Standards

### Commit-Format (Conventional Commits)
```
type(scope): description

[optional body]

[optional footer]
```

### Commit-Types
- `feat`: Neue Features
- `fix`: Fehlerbehebungen
- `docs`: Dokumentation
- `style`: Code-Formatierung
- `refactor`: Code-Umstrukturierung
- `test`: Tests
- `chore`: Wartung, Dependencies
- `ci`: CI/CD-Änderungen
- `perf`: Performance-Verbesserungen

### Beispiele
```
feat(api): add new batch processing endpoint
fix(pose_estimation): correct memory leak in frame analysis
docs(readme): update enterprise development setup
test(unit): add coverage for edge cases in video processing
style(black): apply automatic code formatting
refactor(services): improve error handling consistency
```

## 📚 Dokumentation Standards

### Code-Dokumentation
```python
def process_frame(frame: np.ndarray, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verarbeitet einen einzelnen Frame mit AI-Algorithmen.

    Args:
        frame: NumPy Array mit Bilddaten (H, W, C)
        config: Konfigurationsdictionary mit Processing-Parametern
            - model_name: Name des zu verwendenden AI-Modells
            - threshold: Confidence-Threshold für Detektionen

    Returns:
        Dictionary mit Analyseergebnissen:
            - detections: Liste der gefundenen Objekte
            - confidence: Durchschnittliche Confidence
            - processing_time: Verarbeitungszeit in ms

    Raises:
        ValueError: Bei ungültigen Eingabeparametern
        RuntimeError: Bei AI-Model-Fehlern

    Example:
        >>> frame = np.random.rand(480, 640, 3)
        >>> config = {"model_name": "yolo", "threshold": 0.5}
        >>> result = process_frame(frame, config)
        >>> print(result["detections"])
    """
    pass
```

### API-Dokumentation
- **OpenAPI/Swagger:** Automatische API-Dokumentation
- **API.md:** Händische API-Übersicht
- **Examples:** Code-Beispiele für alle Endpoints

## 🔒 Security Standards

### Security-Checks (Verbindlich)
```bash
# Security-Validierung
make test-security      # Bandit + Safety Scans
make security-audit     # Umfassende Security-Prüfung
```

### Security-Anforderungen
- **Dependency Scanning:** Automatische Vulnerability-Checks
- **Code Scanning:** Bandit für Python Security-Issues
- **Secrets:** Keine Secrets in Code committen
- **Authentication:** Sichere API-Authentifizierung

## 📈 Performance Standards

### Performance-Tests
```bash
# Performance-Validierung
make test-performance   # Load Testing
make benchmark         # Performance-Benchmarks
```

### Performance-Anforderungen
- **Response Time:** <200ms für API-Calls
- **Throughput:** >100 Requests/Sekunde
- **Memory:** <1GB RAM pro Service
- **CPU:** <80% CPU-Auslastung unter Last

## 🤝 Community und Support

### Kommunikation
- **Issues:** GitHub Issues für Bugs und Features
- **Discussions:** GitHub Discussions für Fragen
- **Code Review:** Pull Request Reviews

### Learning Resources
- **Development Rules:** `.cursorrules/rules/` - Detaillierte Regel-Dokumentation
- **Examples:** `examples/` - Code-Beispiele und Tutorials
- **API Docs:** `API.md` - Umfassende API-Dokumentation

## 📄 Lizenz

Mit der Einreichung eines Pull Requests stimmen Sie zu, dass Ihre Änderungen unter der MIT-Lizenz veröffentlicht werden.

---

**Enterprise Development Framework:** 5 Hauptentwicklungsregeln
**Status:** Production-Ready Development Environment
**Support:** Umfassende Automatisierung und Diagnose-Tools

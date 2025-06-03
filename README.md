# AI Media Analysis System

[![AI Media Analysis Test Suite](https://github.com/Paddel87/ai_media_analysis/actions/workflows/tests.yml/badge.svg)](https://github.com/Paddel87/ai_media_analysis/actions/workflows/tests.yml)
[![Linter Compliance](https://github.com/Paddel87/ai_media_analysis/actions/workflows/linter-compliance.yml/badge.svg)](https://github.com/Paddel87/ai_media_analysis/actions/workflows/linter-compliance.yml)
[![venv Environment](https://github.com/Paddel87/ai_media_analysis/actions/workflows/venv-validation.yml/badge.svg)](https://github.com/Paddel87/ai_media_analysis/actions/workflows/venv-validation.yml)

**Status:** Alpha 0.5.0 - Enterprise-Grade Development Framework
**Architektur:** VPS-Orchestrierung + Cloud GPU Computing
**Service-Struktur:** 24 Services in einheitlicher services/ Architektur
**Development-Framework:** 5 Hauptentwicklungsregeln implementiert ✅
**Code-Quality:** Vollautomatische Linter-Compliance mit 7-Tool-Pipeline
**Environment:** Verbindliche venv-Isolation für alle Entwicklungstätigkeiten
**Deployment-Ziel:** VPS/Dedizierte Server ohne eigene GPU
**CI/CD:** Enterprise-Grade Qualitätssicherung
**Development-Environment:** Vollautomatisiert und Production-Ready

## Überblick

Das AI Media Analysis System ist ein **Cloud-Native Microservices-System** zur automatisierten Analyse von Medieninhalten mit **enterprise-grade Entwicklungsstandards**. Das System ist für **Deployment auf VPS/dedizierten Servern ohne eigene GPU** optimiert und nutzt **Cloud GPU-Services** für AI-Processing.

### Alpha 0.5.0 - Enterprise Development Framework ✅

**🎯 5 Hauptentwicklungsregeln erfolgreich implementiert:**

1. **✅ Feature Testing Regel** - Umfassende Test-Pipeline
   - Unit Tests mit 80%+ Coverage-Anforderung
   - Integration Tests zwischen Services
   - End-to-End Tests für vollständige Workflows
   - Performance Tests und Load Testing
   - Security Tests und Vulnerability Scans

2. **✅ Black Standard Regel** - Automatische Code-Formatierung
   - Verbindliche Black-Formatierung (88 Zeichen)
   - Automatische isort Import-Sortierung
   - Pre-commit Hooks für automatische Formatierung
   - CI/CD-Integration mit Format-Checks

3. **✅ Konfigurationsdatei-Validierung** - Config-Qualitätssicherung
   - Syntaktische Validierung aller Config-Dateien
   - Duplikate-Erkennung und -Reparatur
   - Konsistenz-Checks zwischen Konfigurationen
   - Automatische Reparatur-Tools

4. **✅ Linter-Compliance-Regel** - 7-Tool-Qualitäts-Pipeline
   - Black, isort, flake8, mypy, bandit, safety, config-validation
   - 3-Level-Compliance-System (MINIMUM → RECOMMENDED → EXCELLENCE)
   - Automatische Reparatur-Funktionen
   - GitHub Actions Integration

5. **✅ venv-Entwicklungsumgebung-Regel** - Environment-Isolation
   - Verbindliche venv-Nutzung für alle Entwicklungstätigkeiten
   - Automatisches venv-Setup und Health-Monitoring
   - Cross-Platform-Kompatibilität (Windows/Linux/macOS)
   - IDE-Integration und Dependency-Management

**🚀 Enterprise-Features:**
- **Automatische Qualitätssicherung:** Vollintegrierte Linter-Pipeline
- **Reproduzierbare Umgebungen:** venv-Isolation mit Gesundheits-Monitoring
- **Umfassende Test-Coverage:** Multi-Level-Testing-Framework
- **CI/CD-Integration:** GitHub Actions für alle Qualitäts-Gates
- **Development-Automation:** 50+ Makefile-Targets für alle Workflows

### Alpha 0.4.2 - Service-Architektur-Optimierung ✅

**Service-Strukturierung:**
- ✅ **Einheitliche services/ Architektur:** 24 Services in standardisierter Struktur
- ✅ **Root-Level-Duplikate beseitigt:** 11 redundante Verzeichnisse entfernt
- ✅ **Modulare Service-Organisation:** Infrastructure, AI Processing, Management, UI Services
- ✅ **PowerShell & Bash Scripts:** Automatisierte Strukturbereinigung für Windows/Linux
- ✅ **Improved Modularität:** Template-Pattern für zukünftige Service-Erweiterungen
- ✅ **Docker-Compose-Konsistenz:** Alle Services über services/ Pfade referenziert

## Enterprise Development Framework

### 🔧 Entwicklungsumgebung Setup

#### 1. Verbindliche venv-Aktivierung
```bash
# venv erstellen und aktivieren (VERPFLICHTEND)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Automatisches Setup
make venv-setup
```

#### 2. Development-Dependencies installieren
```bash
# Im aktivierten venv
make venv-install-dev   # Development-Tools
make venv-install-test  # Test-Framework
make venv-install-all   # Alle Dependencies
```

#### 3. IDE-Konfiguration
```bash
# Automatische VS Code/Cursor Settings
make venv-setup  # Erstellt .vscode/settings.json automatisch
```

### 🧪 Testing Framework

#### Umfassende Test-Pipeline
```bash
# Alle Tests (EMPFOHLEN)
make test

# Spezifische Test-Types
make test-unit          # Unit Tests (80%+ Coverage)
make test-integration   # Service-Integration Tests
make test-e2e          # End-to-End Workflows
make test-performance  # Performance und Load Tests
make test-security     # Security Scans

# Test-Validierung
make test-validate     # Prüft Test-Anforderungen für neue Features
make test-quality-gate # Quality Gate für Deployment
```

#### Test-Coverage-Anforderungen
- **Unit Tests:** Minimum 80% Coverage
- **Integration Tests:** Alle Service-Interaktionen
- **E2E Tests:** Kritische User-Workflows
- **Performance Tests:** Load Testing unter realistischen Bedingungen

### 🎨 Code-Qualität und Formatierung

#### Automatische Formatierung (Verbindlich)
```bash
# Automatische Formatierung
make format             # Black + isort
make fix-all           # Format + Lint + Config Fix

# Format-Checks
make check-format      # Nur prüfen ohne Änderungen
make format-check-strict # Strenger Check für CI/CD
```

#### Linter-Compliance-Pipeline
```bash
# Vollständige Compliance-Prüfung
make check-compliance

# Spezifische Checks
make check-compliance-critical  # Nur kritische Checks
make fix-compliance            # Automatische Reparatur
make compliance-report         # Detaillierter Report

# Compliance-Hilfe
make lint-help         # Alle verfügbaren Befehle
make compliance-help   # Compliance-Level-Übersicht
```

#### 3-Level-Compliance-System
- **🎯 MINIMUM:** Black, isort, flake8, Config-Validierung (CI/CD-Requirement)
- **⚠️ RECOMMENDED:** + mypy, bandit, safety (Development Standard)
- **🎉 EXCELLENCE:** Alle Checks + 100% Test Coverage (Production Ready)

# HINWEIS: DSGVO, BSI, EU-Compliance, Audit, Datenschutz oder Behördenvorgaben sind für dieses Projekt nicht bindend und werden nicht geprüft. Alle gegenteiligen Aussagen sind ungültig.

### 🔍 venv-Environment-Management

#### venv-Gesundheitsüberwachung
```bash
# venv-Status und Gesundheit
make venv-check         # Umfassender Gesundheitscheck
make venv-status        # Schneller Status-Check
make venv-doctor        # Diagnose-Tool bei Problemen

# venv-Management
make venv-clean-rebuild # venv neu erstellen
make venv-sync         # Dependencies synchronisieren
make venv-security     # Security-Check der Dependencies
```

#### Automatische Validierung
- **Gesundheits-Score:** 0-100 Punkte mit automatischen Verbesserungsvorschlägen
- **Dependency-Tracking:** Überwachung von Package-Versionen und Security-Updates
- **Platform-Diagnose:** Cross-Platform-Kompatibilität

### 🏗️ Konfigurationsdatei-Management

#### Automatische Validierung
```bash
# Konfigurationsdatei-Checks
make validate-config           # Alle Config-Dateien
make check-pytest-ini         # pytest.ini spezifisch
make check-pyproject          # pyproject.toml
make check-docker-compose     # docker-compose.yml

# Automatische Reparatur
make fix-config              # Config-Reparatur
make config-health-check     # Umfassende Config-Prüfung
```

### 📊 Continuous Integration

#### GitHub Actions Workflows
- **🧪 Test Suite:** Umfassende Test-Pipeline bei jedem Push
- **🔍 Linter Compliance:** Automatische Code-Qualitätsprüfung
- **🐍 venv Validation:** Environment-Validierung in CI/CD
- **📋 Quality Gates:** Merge-Blocking bei kritischen Failures

#### Pre-Commit Hooks
```bash
# Pre-commit Setup
make pre-commit-install    # Hooks installieren
make pre-commit-run       # Manuell ausführen
```

### Service-Struktur (Alpha 0.4.2)
```
services/
├── Infrastructure Services (VPS)
│   ├── nginx/              # Load Balancer & SSL Termination
│   ├── vector_db/          # CPU-optimized Vector Database
│   └── redis/              # Message Queue & Cache
├── AI Processing Services (Cloud AI-ready)
│   ├── pose_estimation/    # Human Pose Detection
│   ├── ocr_detection/      # Text Recognition
│   ├── clip_nsfw/          # Content Moderation
│   ├── face_reid/          # Face Recognition
│   └── whisper_transcriber/ # Audio Transcription
├── Management Services
│   ├── job_manager/        # Task Orchestration
│   ├── control/            # System Control
│   ├── embedding_server/   # Vector Embeddings
│   └── llm_service/        # Language Model Interface
├── UI Services
│   ├── ui/                 # Production Web Interface
│   └── streamlit_ui/       # Development Interface
└── common/                 # Shared Components
    ├── logging_config.py   # Standardized Logging
    ├── redis_config.py     # Redis Integration
    └── error_handler.py    # Error Management
```

### Enterprise Development-Workflow

#### 1. Täglicher Workflow (Verbindlich)
```bash
# 1. venv aktivieren
.venv\Scripts\activate

# 2. Umgebung validieren
make venv-check

# 3. Services starten
make quick-start

# 4. Code-Entwicklung...

# 5. Qualitätssicherung vor Commit
make check-compliance      # Linter-Compliance
make test-unit            # Unit Tests
make fix-all              # Automatische Reparaturen

# 6. Pre-Merge Validation
make pre-merge-check      # Vollständiger Quality Gate
```

#### 2. Feature-Entwicklung
```bash
# 1. Feature-Anforderungen validieren
make test-validate        # Test-Anforderungen prüfen

# 2. Entwicklung mit kontinuierlicher Qualitätsprüfung
make test-watch          # Kontinuierliche Tests
make format-with-venv    # Formatierung mit venv-Check

# 3. Quality Gate vor Feature-Abschluss
make test-quality-gate   # Deployment-Readiness
make compliance-gate     # Vollständige Compliance
```

#### 3. Release-Vorbereitung
```bash
# 1. Umfassende Validierung
make release-compliance  # Release Compliance Audit
make test-ci            # CI/CD Pipeline simulieren

# 2. Documentation und Reports
make test-report        # Umfassender Test-Report
make compliance-report  # Compliance-Zusammenfassung
```

### VPS-Optimierte Development-Architektur

#### Local Development Environment
- **Enterprise Setup:** Vollautomatisiertes `make venv-setup` für alle Dependencies
- **Core Services:** Redis, Vector-DB, Nginx mit Health-Monitoring
- **Resource-Optimized:** Memory-Limits für 8GB-16GB Development-Hardware
- **Service-Isolation:** Jeder Service läuft unabhängig mit eigenen Health-Checks
- **Quality Assurance:** Integrierte Linter-Pipeline und Test-Framework
- **Environment-Isolation:** Verbindliche venv-Nutzung mit automatischer Validierung

#### Cloud AI Services (Production-Ready)
- **Computer Vision:** Pose Estimation, OCR, NSFW-Detection
- **Face Recognition:** Face Detection und Re-Identification
- **Audio Processing:** Whisper-basierte Transkription
- **Content Analysis:** CLIP-basierte Content-Klassifikation
- **GPU-Management:** Dynamische Vast.ai Instanz-Allokation

### Development-Environment Setup

#### Enterprise-Grade Setup (Empfohlen)
```bash
# 1. venv erstellen und aktivieren (VERPFLICHTEND)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# 2. Automatisches Enterprise-Setup
make venv-setup

# 3. Compliance validieren
make check-compliance

# 4. Services starten
make quick-start

# 5. Vollständige Tests
make test
```

#### Bestehende Entwickler (Migration)
```bash
# 1. venv-Migration
make venv-clean-rebuild

# 2. Compliance-Update
make fix-compliance

# 3. IDE neu konfigurieren
# VS Code/Cursor: Python Interpreter → .venv/Scripts/python.exe wählen
```

### VPS-Requirements für Development

#### Minimale Development-Spezifikationen
- **CPU:** 4 Cores (Intel/AMD x64)
- **RAM:** 8GB (16GB empfohlen)
- **Storage:** 50GB SSD
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 11+
- **Python:** 3.11+ (für venv-Regel)
- **Docker:** Docker Desktop oder Docker Engine + Docker Compose

#### Empfohlene Development-Spezifikationen
- **CPU:** 8 Cores
- **RAM:** 16GB
- **Storage:** 100GB SSD
- **Network:** Breitband für Cloud AI-Integration
- **IDE:** VS Code/Cursor mit Python-Extension

### Hilfe und Support

#### Development-Hilfe
```bash
# Framework-Hilfe
make help               # Alle verfügbaren Befehle
make venv-help         # venv-Management
make test-help         # Testing Framework
make lint-help         # Code-Qualität
make compliance-help   # Compliance-System

# Diagnose-Tools
make venv-doctor       # venv-Probleme
make test-debug        # Test-Debugging
make monitor           # Service-Monitoring
```

#### Dokumentation
- **Development Rules:** `.cursorrules/rules/` - Detaillierte Regel-Dokumentation
- **API Documentation:** `API.md` - Service-APIs und Endpoints
- **Contributing:** `CONTRIBUTING.md` - Beitrag-Guidelines
- **Changelog:** `CHANGELOG.md` - Versions-Historie

### Enterprise Features (Ready)
- **✅ Multi-Level-Testing:** Unit, Integration, E2E, Performance, Security
- **✅ Automated Quality Assurance:** 7-Tool-Linter-Pipeline
- **✅ Environment-Isolation:** venv-Management mit Health-Monitoring
- **✅ CI/CD-Integration:** GitHub Actions für alle Quality Gates
- **✅ Cross-Platform:** Windows/Linux/macOS kompatibel
- **✅ Reproducible Builds:** Standardisierte Development-Umgebungen

---

**Entwicklung:** Enterprise-Grade Framework mit 5 Hauptentwicklungsregeln
**Status:** Production-Ready Development Environment
**Next:** Production Deployment auf VPS mit Cloud AI-Integration

## Systemvoraussetzungen

- **Python-Version:** 3.11 oder höher (empfohlen und getestet)
- Alle Kernabhängigkeiten und Services sind für Python 3.11+ validiert.
- Für Windows, Linux und macOS geeignet.

**Hinweis:**
Bitte stelle sicher, dass du ein aktuelles Python 3.11.x verwendest. Ältere Versionen (<3.11) werden nicht offiziell unterstützt und können zu Kompatibilitätsproblemen führen.

## Dependency-Management

Alle Abhängigkeiten werden modular in `requirements/` verwaltet:

- **Basis:** `requirements/base.txt`
- **Entwicklung:** `requirements/development.txt`
- **Testing:** `requirements/testing.txt`
- **Service-spezifisch:** z.B. `requirements/services/vision.txt`, `requirements/services/llm.txt`, ...

**Installation (Beispiele):**

```bash
# Entwicklung
pip install -r requirements/development.txt

# Testing
pip install -r requirements/testing.txt

# Service-spezifisch (z.B. Vision)
pip install -r requirements/services/vision.txt
```

**Security-Check:**

```bash
safety check
pip-audit
```

Alle Pakete sind für Python 3.11+ getestet und abgestimmt.

**Hinweis:**
Nach Änderungen an den requirements bitte immer ausführen:

```bash
pip install -U pydantic pydantic-settings
```

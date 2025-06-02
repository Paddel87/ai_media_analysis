# AI Media Analysis System

[![AI Media Analysis Test Suite](https://github.com/Paddel87/ai_media_analysis/actions/workflows/tests.yml/badge.svg)](https://github.com/Paddel87/ai_media_analysis/actions/workflows/tests.yml)

**Status:** Alpha 0.4.0 - VPS-Development-Ready mit stabiler Entwicklungsumgebung  
**Architektur:** VPS-Orchestrierung + Cloud GPU Computing  
**Deployment-Ziel:** VPS/Dedizierte Server ohne eigene GPU  
**CI/CD:** Stabil (GitHub Actions funktionsfähig)  
**Development-Environment:** Vollautomatisiert und VPS-optimiert  

## Überblick

Das AI Media Analysis System ist ein **Cloud-Native Microservices-System** zur automatisierten Analyse von Medieninhalten. Das System ist für **Deployment auf VPS/dedizierten Servern ohne eigene GPU** optimiert und nutzt **Cloud GPU-Services** für AI-Processing.

### Alpha 0.4.0 - Development-Stabilität erreicht ✅

**Neue Development-Features:**
- ✅ **Vollautomatisiertes Setup:** `make dev-setup` für komplette Development-Umgebung
- ✅ **VPS-Optimierte Docker-Compose:** CPU-only Services mit optimierten Resource-Limits
- ✅ **Environment-Management:** Standardisierte Konfiguration über config/environment.example
- ✅ **Development-Scripts:** Automatisierte Setup, Quick-Start und Reset-Scripts
- ✅ **Service-Monitoring:** Comprehensive Health-Checks und Continuous Monitoring
- ✅ **Windows-Kompatibilität:** PowerShell-friendly Development-Workflow

**Bestätigte Funktionalität:**
- ✅ **Docker-Compose System:** VPS-optimiert, läuft stabil auf Standard-Hardware
- ✅ **Redis Service:** Läuft stabil als Message Queue/Cache mit Health-Monitoring
- ✅ **Vector-DB Service:** CPU-only mit faiss-cpu und PyTorch CPU-Versionen
- ✅ **Build-Prozesse:** Systematisches Pattern für VPS-kompatible Services
- ✅ **CI/CD Pipeline:** 57/61 Tests erfolgreich, automatisierte Quality Gates
- ✅ **Development-Tools:** Makefile, run_tests.py, pytest-Suite vollständig

**Strategische Architektur:**
- 🎯 **VPS-First Development:** Optimiert für lokale Entwicklung auf Standard-Hardware
- 🎯 **Cloud AI-Processing:** Vast.ai Integration für GPU-intensive Tasks
- 🎯 **Cost-Efficient:** Keine teure GPU-Hardware für Development erforderlich
- 🎯 **Auto-Setup:** <5 Minuten von Git-Clone zu laufendem System

### VPS-Optimierte Development-Architektur

#### Local Development Environment
- **Quick Setup:** Vollautomatisiertes `make dev-setup` für alle Dependencies
- **Core Services:** Redis, Vector-DB, Nginx mit Health-Monitoring
- **Resource-Optimized:** Memory-Limits für 8GB-16GB Development-Hardware
- **Service-Isolation:** Jeder Service läuft unabhängig mit eigenen Health-Checks
- **Logging:** Structured Logging für alle Services mit Rotation
- **Monitoring:** Real-time Service-Status und Resource-Monitoring

#### Cloud AI Services (Production-Ready)
- **Computer Vision:** Pose Estimation, OCR, NSFW-Detection
- **Face Recognition:** Face Detection und Re-Identification  
- **Audio Processing:** Whisper-basierte Transkription
- **Content Analysis:** CLIP-basierte Content-Klassifikation
- **GPU-Management:** Dynamische Vast.ai Instanz-Allokation

#### Enterprise Features (Version 1.0+)
- **Multi-User-Management:** RBAC und Tenant-Isolation
- **Cost-Optimization:** Auto-Scaling Cloud AI nach Bedarf
- **Analytics:** Usage-Tracking und Performance-Monitoring
- **Security:** SSL, API-Keys, Audit-Logging

### Development-Environment Setup

#### Automatisiertes Setup (Empfohlen)
```bash
# Ein-Kommando Setup für komplette Development-Umgebung
make dev-setup

# Oder für schnelles minimal Setup
make quick-setup

# Services starten
make quick-start

# Tests ausführen
make test
```

#### Manuelles Setup
```bash
# Dependencies installieren
pip install -r requirements.txt
pip install -r requirements-ci.txt

# Environment konfigurieren
cp config/environment.example .env
# .env editieren für lokale Konfiguration

# Core Services starten
make run-core-services

# Health Check
make health-check-core
```

### Development-Workflow

#### Täglicher Development-Workflow
```bash
# 1. Services starten
make quick-start

# 2. Code ändern...

# 3. Tests ausführen
make test-fast

# 4. Code formatieren
make format

# 5. Pre-commit checks
make pre-commit

# 6. Services neu starten bei Bedarf
make restart-core
```

#### Service-spezifische Entwicklung
```bash
# Nur bestimmte Services starten
make run-core-services   # Redis, Vector-DB, Nginx
make run-ai-services     # AI-Services starten

# Service-spezifische Tests
make test-redis         # Redis funktionalität
make test-vector-db     # Vector Database
make test-nginx         # Nginx Proxy-Konfiguration

# Logs anzeigen
make logs-core          # Core Service Logs
make logs-ai            # AI Service Logs
make monitor            # Continuous monitoring
```

### VPS-Requirements für Development

#### Minimale Development-Spezifikationen
- **CPU:** 4 Cores (Intel/AMD x64)
- **RAM:** 8GB (16GB empfohlen)
- **Storage:** 50GB SSD
- **OS:** Windows 10+, Ubuntu 20.04+, macOS 11+
- **Docker:** Docker Desktop oder Docker Engine + Docker Compose

#### Empfohlene Development-Spezifikationen  
- **CPU:** 8 Cores
- **RAM:** 16GB
- **Storage:** 100GB SSD
- **Network:** Breitband für Cloud AI-Integration

### Production VPS-Deployment

#### VPS-Vorbereitung
```bash
# VPS-Setup (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y
sudo apt install docker.io docker-compose-v2 git make -y
sudo usermod -aG docker $USER

# Repository klonen und Setup
git clone https://github.com/your-repo/ai_media_analysis.git
cd ai_media_analysis
make vps-setup
```

#### Production-Deployment  
```bash
# VPS-optimierte Services bauen und starten
make vps-deploy
make run-core-services

# Health Check
make health-check-core

# SSL-Setup für Production
# TODO: SSL-Konfiguration dokumentieren
```

## Development-Roadmap

### Alpha 0.4.0 ✅ - Development-Stabilität (ERREICHT)
**Ziel:** Stabile lokale Entwicklungsumgebung  
**Erreicht:**
- Vollautomatisiertes Development-Setup
- VPS-optimierte Docker-Compose-Konfiguration
- Comprehensive Service-Monitoring
- Windows/Linux/macOS Kompatibilität

### Alpha 0.5.0 (2-3 Wochen)
**Ziel:** Production-Ready VPS-Setup  
**Roadmap:**
- CPU-Dockerfiles für alle AI-Services
- SSL-Termination und Production-Nginx-Setup
- Automated VPS-Deployment-Scripts
- Performance-Benchmarks für VPS-Hardware

### Alpha 0.6.0 (4-6 Wochen)  
**Ziel:** Cloud AI-Integration  
**Roadmap:**
- Vast.ai API-Integration
- Seamless VPS ↔ Cloud Communication
- Auto-Scaling und Cost-Optimization
- Fallback-Mechanismen

### Beta 0.7.0 (3-4 Monate)
**Ziel:** Feature-Vollständigkeit  
**Roadmap:**
- Alle AI-Features über Cloud verfügbar
- End-to-End Workflows
- Enterprise-Security-Features

### Version 1.0 (12-18 Monate)
**Ziel:** Multi-Tenant Platform  
**Features:**
- Multi-User-Management
- Usage-Analytics und Billing
- Optional: Dedicated GPU-Server-Integration

## Development-Tools und -Befehle

### Häufige Entwicklungsbefehle
```bash
# Setup und Start
make help                   # Alle verfügbaren Befehle anzeigen
make dev-setup             # Komplette Development-Umgebung
make quick-start           # Services schnell starten
make vps-setup             # VPS-Environment vorbereiten

# Services Management
make run-core-services     # Nur Core-Services starten
make run-ai-services       # AI-Services starten
make stop-services         # Alle Services stoppen
make restart-core          # Core-Services neu starten

# Testing und Quality
make test                  # Alle Tests ausführen
make test-fast             # Nur schnelle Unit Tests
make test-coverage         # Tests mit Coverage-Analyse
make format                # Code formatieren
make lint                  # Code-Linting
make pre-commit            # Pre-commit Checks

# Monitoring und Debugging
make health-check          # Service-Health prüfen
make monitor               # Continuous Service-Monitoring
make logs                  # Alle Service-Logs anzeigen
make logs-core             # Nur Core-Service-Logs

# Utilities
make clean                 # Temporäre Dateien bereinigen
make clean-docker          # Docker-Artefakte bereinigen
make reset-dev             # Komplette Development-Umgebung zurücksetzen
```

### Environment-Konfiguration
```bash
# Environment aus Template erstellen
cp config/environment.example .env

# Wichtige Einstellungen für lokale Entwicklung:
DEPLOYMENT_MODE=local       # Lokaler Development-Modus
CLOUD_MODE=false           # Cloud AI deaktiviert für lokale Dev
LOG_LEVEL=INFO             # Ausführliches Logging
DEBUG=true                 # Debug-Modus aktiviert
```

## VPS-Provider Empfehlungen

### Development (Budget)
- **Hetzner:** €20-40/Monat, Deutschland, sehr stabil
- **DigitalOcean:** $20-48/Monat, global verfügbar
- **Linode:** $12-48/Monat, developer-friendly

### Production (Business)
- **Hetzner Dedicated:** €60-100/Monat, hohe Performance
- **AWS EC2:** Variable Kosten, Enterprise-Features
- **Google Cloud:** Variable Kosten, AI-Integration

## Status-Dokumentation

Detaillierte Informationen zum aktuellen Projektstatus:
- [PROJECT_STATE.md](PROJECT_STATE.md) - VPS-Deployment-Strategie und aktuelle Tasks
- [STATUS.md](STATUS.md) - Entwicklungsphase und realistische Roadmap
- [CHANGELOG.md](CHANGELOG.md) - Vollständige Versionshistorie mit Development-Features
- [DEVELOPMENT_STRATEGY](DEVELOPMENT_STRATEGY) - Langfristige Entwicklungsstrategie

## Beitragen

Das Projekt ist in aktiver Alpha-Entwicklung mit Fokus auf VPS-Development-Stabilität:

### Entwicklungsrichtlinien
- **VPS-First:** Alle Features für Standard-Server optimieren
- **Development-Stabilität:** Lokaler Workflow muss zuverlässig funktionieren
- **Test-First:** Keine Features ohne entsprechende Tests
- **Dokumentation:** Jede Änderung muss dokumentiert werden

### Contribution-Workflow
```bash
# 1. Development-Environment setup
make dev-setup

# 2. Feature-Branch erstellen
git checkout -b feature/your-feature

# 3. Entwickeln mit kontinuierlichen Tests
make test-fast

# 4. Pre-commit checks
make pre-commit

# 5. Pull Request mit Tests und Dokumentation
```

## Lizenz

[Lizenz-Information hier einfügen]
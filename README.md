# AI Media Analysis System

**VPS-Native Content-Moderation-Platform**
**Version:** 0.1.0
**Status:** Einfaches Development-Framework
**Deployment:** VPS-optimiert für remote access
**Zielgruppe:** Content-Moderatoren

---

## 🎯 **PROJECT MISSION**

**Einfache VPS Content-Moderation-Platform** - Content-Moderatoren können VPS einrichten und haben Zugriff auf AI-Media-Analysis.

**UC-001 Enhanced Manual Analysis:** Erstes Nutzungskonzept

### 0.1.0 - Einfaches Development Framework ✅

**🎯 DEVELOPMENT-STANDARDS:**

1. **✅ Testing:** Einfache Test-Pipeline
2. **✅ Code-Standard:** Automatische Formatierung
3. **✅ Config-Validierung:** Basis Konfigurationsprüfung
4. **✅ Code-Quality:** Standard Linting
5. **✅ Environment:** venv-Nutzung

**🚀 FEATURES:**
- **Makefile-Targets:** Workflow-Automatisierung
- **GitHub Actions:** Basis Quality Checks
- **Cross-Platform:** Windows/Linux/macOS Support
- **Linter-Pipeline:** black, isort, flake8, mypy

## Überblick

Das AI Media Analysis System ist ein **Microservices-System** zur automatisierten Analyse von Medieninhalten. Das System ist für **Deployment auf VPS** optimiert und nutzt **Cloud Services** für AI-Processing.

### Service-Struktur
```
services/
├── infrastructure/     # Core Services
│   ├── nginx/         # Load Balancer
│   ├── redis/         # Cache & Queue
│   └── vector_db/     # Embeddings
├── ai_processing/     # AI Services
│   ├── pose_estimation/     # Pose Detection
│   ├── ocr_detection/       # Text Recognition
│   ├── clip_nsfw/          # Content Safety
│   ├── face_reid/          # Face Recognition
│   └── whisper_transcriber/ # Audio Processing
└── management/        # APIs
    ├── job_manager/   # Task Management
    ├── control/       # System Control
    └── llm_service/   # Language Models
```

## Development Framework

### 🔧 Setup

#### 1. venv Setup
```bash
# venv erstellen und aktivieren
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Automatisches Setup
make setup
```

#### 2. Dependencies installieren
```bash
# Im aktivierten venv
pip install -r requirements.txt
```

### 🧪 Testing

#### Test-Pipeline
```bash
# Alle Tests
make test

# Spezifische Tests
make test-unit          # Unit Tests
make test-integration   # Integration Tests
```

### 🎨 Code-Qualität

#### Automatische Formatierung
```bash
# Formatierung
make format             # Black + isort

# Checks
make lint              # Linting
```

### Development-Environment Setup

#### Standard Setup
```bash
# 1. venv aktivieren
python -m venv .venv
.venv\Scripts\activate  # Windows

# 2. Dependencies
pip install -r requirements.txt

# 3. Services starten
make start

# 4. Tests
make test
```

### VPS-Requirements

#### Minimale Spezifikationen
- **CPU:** 4 Cores
- **RAM:** 8GB
- **Storage:** 50GB SSD
- **OS:** Ubuntu 20.04+ oder Windows 10+
- **Python:** 3.11+

### Service-Integration

#### Standard Services
- **Redis**: Cache und Queue
- **Vector-DB**: Embeddings
- **AI-Services**: Computer Vision und Audio
- **Job-Manager**: Task-Orchestrierung

---

**Status:** Production-Ready Development Environment
**Next:** Production Deployment auf VPS

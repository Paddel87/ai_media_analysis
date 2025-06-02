# AI Media Analysis System - Architektur-Dokumentation

## Systemübersicht

Das AI Media Analysis System ist eine **verteilte, mikroservice-basierte Anwendung** zur Analyse von Medieninhalten mit verschiedenen KI-Modellen. Das System ist sowohl für **lokale Entwicklung** als auch **VPS-Deployment** optimiert.

### Hauptkomponenten

1. **Vision Pipeline Services**
   - **NSFW-Detection** (`clip_nsfw`, `nsfw_detection`)
   - **Pose Estimation** (`pose_estimation`)
   - **OCR Detection** (`ocr_detection`)
   - **Face Recognition** (`face_reid`)
   - **Restraint Detection** (`restraint_detection`)
   - **Object Review** (`object_review`)

2. **Audio-Analyse Services**
   - **Whisper Transcription** (`whisper_service`, `whisper_transcriber`)
   - **Audio Processing Pipeline**

3. **AI/ML Services**
   - **LLM Service** (`llm_service`, `llm_summarizer`)
   - **CLIP Service** (`clip_service`)
   - **Embedding Server** (`embedding_server`)

4. **Datenverarbeitung**
   - **Vector Database** (`vector_db`) - Qdrant/FAISS
   - **Redis Caching** - Sitzungsmanagement und Caching
   - **Job Manager** (`job_manager`) - Asynchrone Verarbeitung

5. **Infrastructure Services**
   - **Nginx** (`nginx`) - Load Balancer und Reverse Proxy
   - **Data Persistence** - Datenmanagement
   - **Guardrails** (`guardrails`) - Sicherheit und Validierung

6. **User Interface**
   - **Streamlit UI** (`ui`)
   - **Person Dossier** (`person_dossier`) - Personenverwaltung
   - **Control Interface** (`control`) - Systemkontrolle

## Technische Architektur

### Modernisierte Service-Architektur

```
┌─────────────────┐    ┌──────────────────────┐    ┌───────────────────┐
│   Frontend UI   │    │    Load Balancer     │    │   AI Services     │
│   (Streamlit)   │◄──►│      (Nginx)         │◄──►│  Vision/Audio/LLM │
└─────────────────┘    └──────────────────────┘    └───────────────────┘
                                   │
                                   ▼
┌─────────────────┐    ┌──────────────────────┐    ┌───────────────────┐
│   Vector DB     │◄──►│    Job Manager       │◄──►│  Redis Cache      │
│  (Qdrant/FAISS) │    │   (Orchestrierung)   │    │  (Session/Cache)  │
└─────────────────┘    └──────────────────────┘    └───────────────────┘
                                   │
                                   ▼
                       ┌──────────────────────┐
                       │   Data Persistence   │
                       │   (Files/Results)    │
                       └──────────────────────┘
```

### Dependencies & Requirements-Architektur

```
requirements/
├── base.txt           # 🏗️  Core Production Dependencies
├── development.txt    # 🛠️  Development Tools (inherits base)
├── testing.txt        # 🧪 Test Framework (inherits dev)
└── services/
    ├── llm.txt        # 🤖 LLM & Vector DB Dependencies
    ├── vision.txt     # 👁️  Computer Vision Dependencies
    └── cloud.txt      # ☁️  Cloud Storage Dependencies
```

### Komponenten-Details

#### Vision Pipeline Services
- **Technologien**: Python, OpenCV, PyTorch, MMPose, MMDetection
- **GPU-Support**: CUDA-beschleunigt mit CPU-Fallback
- **Batch-Verarbeitung**: Optimiert für Effizienz
- **Caching**: Redis-basiert für wiederholte Analysen
- **Services**: `pose_estimation`, `ocr_detection`, `face_reid`, `nsfw_detection`

#### Audio-Analyse Services
- **Technologien**: Whisper, torchaudio, librosa
- **Real-time**: Stream-Verarbeitung möglich
- **Batch-Mode**: Große Dateien effizient verarbeiten
- **Services**: `whisper_service`, `whisper_transcriber`

#### LLM & AI Services
- **Technologien**: LangChain, OpenAI, Transformers, ChromaDB
- **Vector Search**: Embedding-basierte Suche
- **Services**: `llm_service`, `llm_summarizer`, `embedding_server`, `clip_service`

#### Datenverarbeitung
- **Vector DB**: Qdrant für Production, FAISS für Development
- **Redis**: Caching, Session-Management, Job-Queues
- **Persistence**: File-basierte Datenhaltung mit Backup-Strategien

#### Frontend & Control
- **UI**: Streamlit mit Plotly-Visualisierungen
- **Management**: Personen-Dossiers, System-Kontrolle
- **Responsive**: Mobile-optimiert

## Deployment-Architektur

### Docker-basierte Mikroservices
```yaml
# Jeder Service in eigenem Container
services:
  - nginx           # Load Balancer
  - redis          # Cache & Sessions
  - vector-db      # Vector Search
  - pose_estimation # Computer Vision
  - llm_service    # Language Models
  - whisper_service # Audio Processing
  - ui             # Frontend
```

### VPS-Optimierungen
- **Memory-Limits**: Angepasst für 8GB+ VPS
- **CPU-Quotas**: Effiziente Ressourcenverteilung
- **Health-Checks**: Robust monitoring für alle Services
- **Restart-Policies**: `unless-stopped` für Ausfallsicherheit

#### VPS-spezifisches Resource Management
```yaml
# CPU-Optimierung für VPS
services:
  pose_estimation:
    deploy:
      resources:
        limits: { cpus: '2', memory: '2G' }
        reservations: { cpus: '1', memory: '1G' }
    environment:
      - CPU_ONLY=true
      - MAX_WORKERS=2
      - MEMORY_LIMIT=2G

# Memory-Optimierung
  redis:
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru

# Storage-Optimierung
  vector-db:
    volumes:
      - vector_data:/app/data  # Persistent storage
    environment:
      - DISK_CACHE_SIZE=512MB
```

#### Cost-Efficiency Strategien
- **Dynamic Resource Allocation**: Services nur bei Bedarf skalieren
- **Resource Sharing**: Effiziente Nutzung von CPU/Memory zwischen Services
- **Auto-Cleanup**: Automatische Bereinigung von temporären Daten
- **Load-Based Scaling**: Services basierend auf tatsächlicher Last starten/stoppen

#### VPS Auto-Scaling
```bash
# Scaling-Commands
make scale-up-ai      # AI Services bei hoher Last
make scale-down-ai    # AI Services bei niedriger Last
make vps-optimize     # Automatische Ressourcen-Optimierung
make cost-monitor     # Cost-Tracking und -Optimierung
```

### Ressourcen-Management
```yaml
# Beispiel Ressourcen-Allokation
pose_estimation:
  limits: { cpus: '2', memory: '2G' }
  reservations: { cpus: '1', memory: '1G' }
```

## Development-Architektur

### Modulare Requirements-Installation
```bash
# Service-spezifische Installation
make install-llm      # LLM Dependencies
make install-vision   # Vision Dependencies
make install-cloud    # Cloud Dependencies
make install-all      # Vollständige lokale Entwicklung
```

### Branching-Strategie
- **main**: Produktions-Code
- **experiment/**: Sichere Experimente
- **wip/**: Work-in-Progress Features
- **backup/**: Automatische Backups

### Code-Qualität
- **Black + isort**: Automatische Formatierung
- **Flake8 + mypy**: Linting und Type-Checking
- **Pre-commit hooks**: Automatisierte Qualitätschecks
- **Pytest**: Umfassende Test-Suite

## Sicherheit & Compliance

### API-Sicherheit
- **Authentifizierung**: Token-basiert
- **Rate Limiting**: Nginx-basiert
- **Input Validierung**: Pydantic-Schemas
- **CORS**: Konfigurierbare Policies

### Daten-Sicherheit
- **Verschlüsselung**: TLS/SSL für alle Verbindungen
- **Cloud-Integration**: AWS, GCP, Azure support
- **Backup-Strategien**: Automatisierte Datensicherung
- **Guardrails**: Input/Output-Validierung

## Monitoring & Observability

### Health Monitoring
```bash
# Comprehensive Health Checks
make health-check      # Alle Services
make health-check-core # Core Services nur
make health-check-ai   # AI Services nur
```

### Logging-Architektur
- **Zentralisiertes Logging**: JSON-Format mit Rotation
- **Service-spezifische Logs**: Getrennte Log-Streams
- **Error-Tracking**: Strukturierte Fehlerbehandlung
- **Performance-Monitoring**: Metriken-basiert

### Development-Monitoring
```bash
make monitor          # Live Service Monitoring
make logs-all        # Alle Service Logs
make logs-core       # Core Service Logs
```

### VPS Performance & Cost Monitoring
```bash
# Resource Usage Monitoring
make vps-status       # VPS Resource Usage
make memory-monitor   # Memory Usage Tracking
make cpu-monitor      # CPU Usage Analysis
make storage-monitor  # Disk Usage Tracking

# Cost & Efficiency Monitoring
make cost-analysis    # Resource Cost Analysis
make efficiency-report # Resource Efficiency Report
make scaling-history  # Auto-Scaling History
make resource-alerts  # Proactive Resource Alerts
```

#### VPS-spezifische Metriken
- **CPU-Utilization**: Pro-Service CPU-Nutzung
- **Memory-Efficiency**: Memory-Leak Detection
- **Storage-Usage**: Disk Space Monitoring
- **Network-Traffic**: Bandwidth-Usage Tracking
- **Cost-Per-Service**: Service-basierte Kostenanalyse
- **Scaling-Efficiency**: Auto-Scaling Performance

## Skalierung & Performance

### Horizontale Skalierung
- **Load Balancing**: Nginx mit mehreren Service-Instanzen
- **Service-Replikation**: Docker Swarm ready
- **Database-Sharding**: Vector DB Clustering
- **Cache-Distribution**: Redis Cluster support

### Vertikale Skalierung
- **GPU-Ressourcen**: CUDA-optimiert mit CPU-Fallback
- **Memory-Optimierung**: Lazy Loading und Caching
- **CPU-Optimierung**: Async/Await Patterns
- **Storage-Optimierung**: Komprimierte Speicherung

### Performance-Testing
```bash
make benchmark       # Performance Benchmarks
make stress-test     # System-Stress-Tests
make load-test       # Load Testing
```

## Best Practices & Development

### Code-Architektur
- **Mikroservices**: Lose gekoppelt, stark kohäsiv
- **Dependency Injection**: Konfigurierbare Services
- **Interface Segregation**: Klare API-Contracts
- **Event-Driven**: Asynchrone Kommunikation

### Testing-Strategie
```bash
make test-unit        # Unit Tests
make test-integration # Integration Tests
make test-e2e        # End-to-End Tests
make test-coverage   # Coverage Analysis
```

### Deployment-Pipeline
1. **Development**: Lokale Requirements-Installation
2. **Testing**: Automatisierte Test-Suite
3. **Staging**: VPS-ähnliche Umgebung
4. **Production**: Docker-basiertes Deployment

### Documentation
- **Code**: Inline-Dokumentation + Docstrings
- **API**: Automatisch generierte OpenAPI-Specs
- **Architecture**: Living Documentation (diese Datei)
- **Runbooks**: Operational Procedures

## Technologie-Stack

### Core Technologies
- **Python 3.11+**: Primary Development Language
- **FastAPI**: High-performance API Framework
- **Docker**: Containerization & Orchestration
- **Nginx**: Load Balancing & Reverse Proxy

### AI/ML Stack
- **PyTorch**: Deep Learning Framework
- **Transformers**: HuggingFace Models
- **OpenCV**: Computer Vision
- **Whisper**: Audio Transcription
- **LangChain**: LLM Orchestration

### Data & Storage
- **Redis**: Caching & Session Management
- **Qdrant/FAISS**: Vector Search
- **S3/GCS/Azure**: Cloud Storage Integration
- **SQLAlchemy**: Database ORM (wenn benötigt)

### Development Tools
- **Black + isort**: Code Formatting
- **Flake8 + mypy**: Code Quality
- **Pytest**: Testing Framework
- **Pre-commit**: Git Hooks

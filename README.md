# AI Media Analysis Platform

A comprehensive media analysis platform that leverages artificial intelligence to analyze images and videos for various content types, including NSFW content, poses, text, and restraints.

## 🌟 Features

- **Multi-Service Architecture**: Modular design with specialized services for different analysis tasks
- **Real-time Processing**: Efficient batch processing and frame sampling for video analysis
- **GPU Acceleration**: NVIDIA GPU support for high-performance inference
- **Scalable Infrastructure**: Docker-based deployment with resource management
- **Job Management**: Asynchronous job processing with status tracking
- **RESTful API**: FastAPI-based endpoints for easy integration

## 🏗️ Architecture

### Core Services

- **Vision Pipeline**: Central service coordinating all analysis tasks
- **Job Manager**: Handles job queuing and processing
- **Restraint Detection**: Specialized service for detecting restraints and related materials
- **NSFW Detection**: Content moderation using CLIP-based models
- **Pose Estimation**: Body pose and movement analysis
- **OCR Detection**: Text and logo recognition
- **Face Recognition**: Face detection and re-identification

### Supporting Services

- **Redis**: Message broker and caching
- **Control Service**: System orchestration
- **Streamlit UI**: Web interface for monitoring and control
- **Vector Database**: Efficient storage and retrieval of embeddings

## 🚀 Getting Started

### Prerequisites

### Docker and Docker Compose
- Docker Engine 24.0.0 or later
- Docker Compose v2.20.0 or later
- NVIDIA Container Toolkit

### GPU Support
The system supports various GPU configurations:

#### Local GPU Setup
- Consumer GPUs: RTX 3060, 3070, 3080, 3090, 4070, 4080, 4090
- Professional GPUs: RTX A4000, A5000, A6000
- Data Center GPUs: A100, H100

#### Cloud GPU Options
1. **Data Center GPUs** (Enterprise Cloud Providers)
   - AWS, GCP, Azure: A100, H100
   - Enterprise-grade reliability
   - 24/7 support
   - Higher cost

2. **Consumer GPUs** (Specialized Providers)
   - Vast.ai, RunPod: RTX 3080, 3090, 4080, 4090
   - Cost-effective for development
   - Flexible hourly pricing
   - Good for testing and medium workloads

3. **Professional GPUs** (Mixed Providers)
   - RTX A4000, A5000, A6000
   - Available on both enterprise and specialized providers
   - Balanced performance and cost

### System Requirements
- Minimum 16GB RAM
- 100GB free disk space
- CUDA 12.0 or later
- Ubuntu 20.04/22.04 or Windows 11 with WSL2

### Installation

1. Clone the repository:
   ```

# AI Media Analysis System

Ein umfassendes System zur Analyse von Medieninhalten mit künstlicher Intelligenz.

## Systemanforderungen

### Hardware
- **CPU**: 
  - Mindestens 8 Kerne
  - 3.0 GHz oder schneller
  - AVX2-Unterstützung empfohlen
- **RAM**: 
  - Mindestens 32 GB
  - 64 GB empfohlen für große Batch-Verarbeitungen
- **GPU**: 
  - NVIDIA GPU mit mindestens 8 GB VRAM
  - CUDA 11.7 oder höher
  - Mindestens 2 GPUs für optimale Performance
- **Speicher**: 
  - Mindestens 500 GB SSD
  - NVMe SSD empfohlen
  - Separate Partition für Medien empfohlen

### Software
- **Betriebssystem**:
  - Ubuntu 20.04 LTS oder höher
  - Windows 10/11 Pro mit WSL2
  - Docker Desktop für Windows/Mac
- **Docker**:
  - Version 20.10 oder höher
  - Docker Compose V2
  - NVIDIA Container Toolkit
- **Python**:
  - Version 3.10 oder höher
  - pip 22.0 oder höher
- **Node.js**:
  - Version 18 LTS oder höher
  - npm 9.0 oder höher

### Netzwerk
- **Bandbreite**:
  - Mindestens 100 Mbps
  - 1 Gbps empfohlen
- **Latenz**:
  - < 50ms für optimale Performance
- **Ports**:
  - 80/443 (HTTP/HTTPS)
  - 6379 (Redis)
  - 5432 (PostgreSQL)
  - 6333 (Qdrant)

### Empfohlene Konfiguration
- **Produktionsumgebung**:
  - 2x NVIDIA A100 oder vergleichbar
  - 128 GB RAM
  - 2 TB NVMe SSD
  - 10 Gbps Netzwerk
- **Entwicklungsumgebung**:
  - 1x NVIDIA RTX 3080 oder vergleichbar
  - 64 GB RAM
  - 1 TB NVMe SSD
  - 1 Gbps Netzwerk

### Skalierung
- **Horizontale Skalierung**:
  - Unterstützung für mehrere GPU-Nodes
  - Load Balancing für API-Anfragen
  - Redis Cluster für Caching
  - Qdrant Cluster für Vektorsuche
- **Vertikale Skalierung**:
  - Dynamische GPU-Zuweisung
  - Automatische Batch-Größenanpassung
  - Adaptives Caching

### Monitoring
- **System-Monitoring**:
  - GPU-Auslastung
  - Speichernutzung
  - Netzwerk-Performance
  - Service-Health
- **Anwendungs-Monitoring**:
  - API-Latenz
  - Batch-Verarbeitungszeiten
  - Fehlerraten
  - Ressourcennutzung

### Backup & Recovery
- **Datenbank-Backup**:
  - Tägliche PostgreSQL-Dumps
  - Redis-Persistenz
  - Qdrant-Snapshots
- **System-Backup**:
  - Wöchentliche System-Images
  - Konfigurations-Backups
  - Medien-Archivierung

## Installation

[Installationsanleitung folgt]

## Verwendung

[Verwendungsanleitung folgt]

## Dokumentation

[Link zur Dokumentation folgt]

## Lizenz

[Lizenzinformationen folgt]
# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt der [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2024-03-20

### Added
- Cloud Storage Integration
  - Amazon S3 Unterstützung
  - Google Cloud Storage Integration
  - Azure Blob Storage Anbindung
  - Dropbox Integration
  - MEGA Cloud Storage Support
- Erweiterte UI-Funktionen
  - Cloud Provider Auswahl
  - Sichere Konfigurationsspeicherung
  - Verbesserte Dateilistenansicht
  - Fortschrittsanzeige für Downloads

### Changed
- UI-Überarbeitung für Cloud-Integration
- Verbesserte Fehlerbehandlung
- Erweiterte Dokumentation

### Fixed
- Sichere Handhabung von Zugangsdaten
- Verbesserte Fehlerbehandlung bei Cloud-Verbindungen

## [0.5.0] - 2024-03-19

### Added
- Comprehensive GPU support documentation
- Detailed scaling capabilities for different GPU models
- Cloud integration with Vast.ai and RunPod
- Hybrid deployment options
- Performance optimizations for different GPU types

### Changed
- Updated README.md with detailed English documentation
- Improved GPU acceleration documentation
- Enhanced performance section with GPU-specific details
- Restructured project documentation

### Fixed
- GPU memory management in batch processing
- Documentation inconsistencies
- Service health check endpoints

## [0.4.0] - 2024-03-18

### Added
- Restraint Detection Service
- Integration with Vision Pipeline
- New Docker configurations
- API documentation updates
- Job management features

### Changed
- Renamed services for better clarity
- Updated service dependencies
- Improved error handling
- Enhanced logging system

### Fixed
- Service communication issues
- Resource allocation in Docker
- Health check implementations

## [0.3.0] - 2024-03-17

### Added
- Batch processing optimization
- LRU caching implementation
- Asynchronous processing
- Enhanced error handling
- Improved logging system

### Changed
- Updated NSFW detection
- Modified Vision Pipeline
- Enhanced Docker configurations

### Fixed
- Memory leaks in batch processing
- Service communication issues
- Resource management

## [0.2.0] - 2024-03-16

### Added
- Basic service structure
- Initial Docker setup
- Core functionality

### Changed
- Project organization
- Service architecture

### Fixed
- Initial setup issues
- Configuration problems

## [0.1.0] - 2024-03-15

### Added
- Initial project setup
- Basic documentation
- Core services structure

## [0.4.0] - 2025-05-31
### Hinzugefügt
- Pose Estimation Service implementiert
- Vision Pipeline mit Pose Estimation Integration
- GPU-Beschleunigung für Pose Estimation
- Automatische Ergebnis-Speicherung in JSON-Format
- Detailliertes Logging-System

### Geändert
- Docker-Compose-Konfiguration für GPU-Unterstützung
- Vision Pipeline Architektur optimiert
- Verbesserte Fehlerbehandlung

### Behoben
- GPU-Ressourcen-Management optimiert
- Speicherverwaltung verbessert

## [0.7.0] - 2024-03-21

### Added
- Build-Tools für Docker-Container
  - Installation von build-essential und g++
  - Optimierte Container-Build-Konfiguration

### Changed
- Korrektur der Docker-Build-Pfade
  - Anpassung der Build-Kontexte
  - Korrektur der Dateipfade in Dockerfiles
- Verbesserte requirements.txt Struktur

### Fixed
- Build-Fehler bei mmcv Installation
- Pfadprobleme in Docker-Compose
- Fehlende Build-Abhängigkeiten

## [Unreleased]
### Added
- Integrated missing services:
  - `pose_estimation`
  - `ocr_detection`
  - `clip_nsfw`
  - `face_reid`
  - `whisper_transcriber`
- Extended docker-compose.yml to include all modules
- Created `README.md` placeholders for new services

### Changed
- Updated docker-compose to mount new volumes for extended processing
- `vision_pipeline` now supports image series
- Bereinigung der Docker-Compose Konfiguration
  - Entfernung invalider Volume-Definitionen
  - Vereinfachung der Service-Konfigurationen
  - Optimierung der Netzwerk- und Volume-Einstellungen
  - Verbesserung der Health-Checks für Services

### Pending
- GPU runtime validation
- Inter-service signaling via Redis (jobs, results, scaling triggers)
- Shared logging and healthchecks

### Fixed
- Korrektur der Docker-Compose Validierungsfehler
  - Entfernung von `volumes.face_reid` und `volumes.whisper_transcriber`
  - Bereinigung der Service-Definitionen
  - Korrektur der Volume-Mappings

# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt der [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-03-20

### Hinzugefügt
- Initiale Version des AI Media Analysis Systems
- Implementierung der Vision Pipeline
- NSFW-Detection mit CLIP
- Restraint Detection
- OCR und Logo-Erkennung
- Face Recognition
- Audio-Analyse mit Whisper
- Vektordatenbank-Integration
- Streamlit UI
- Docker-Compose Konfiguration
- Load Balancing mit Nginx
- Redis Caching
- Job Management System

### Geändert
- Optimierte Docker-Compose Konfiguration
- Verbesserte Redis-Konfiguration
- Performance-Optimierungen für Batch-Verarbeitung

### Sicherheit
- Implementierte Health Checks
- Sichere API-Endpunkte
- Verschlüsselte Cloud-Storage-Kommunikation

## [0.9.0] - 2024-03-15

### Hinzugefügt
- Beta-Version der Streamlit UI
- Erste Version der Personendossier-Verwaltung
- Grundlegende Cloud-Integration

### Geändert
- Verbesserte Fehlerbehandlung
- Optimierte Batch-Verarbeitung

## [0.8.0] - 2024-03-10

### Hinzugefügt
- Erste Version der Vision Pipeline
- Basis-Implementierung der AI-Services
- Docker-Containerisierung

### Geändert
- Angepasste Service-Konfigurationen
- Verbesserte Logging-Implementierung

## [1.1.0] - 2024-03-19

### Hinzugefügt
- Vast.ai Integration für GPU-Instanzen
- Dynamische Instanzerstellung und -verwaltung
- Automatische Skalierung basierend auf Last
- SSH-Management für Remote-Zugriff
- Kostenoptimierte Ausführung
- Parallele Modellausführung
- Erweiterte GPU-Typen für verschiedene Anforderungen
- API-Dokumentation
- Beitragsrichtlinien
- Entwicklungsstandards

### Geändert
- Optimierte Modell-Ressourcennutzung
- Verbesserte Batch-Verarbeitung
- Angepasste Skalierungsfaktoren
- Erweiterte Kostenberechnung
- Verbesserte Fehlerbehandlung
- Aktualisierte Dokumentation

### Entfernt
- Statische GPU-Konfiguration
- Feste Instanz-Zuweisung

## [1.0.0] - 2024-03-18

### Hinzugefügt
- Basis-Restraint-Erkennung
- GPU-Optimierungen
- Batch-Verarbeitung
- Caching-System
- API-Endpunkte
- Grundlegende Dokumentation

### Geändert
- Initiale Implementierung
- Basis-Konfiguration

### Entfernt
- Keine

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

## [1.1.0] - 2024-03-21

### Verbessert
- Implementiert verbessertes GPU-Memory-Management in der Vision Pipeline
  - Automatische GPU-Speicherbereinigung basierend auf Zeit und Frame-Counter
  - Dynamische Batch-Größenanpassung basierend auf GPU-Speichernutzung
  - Detailliertes GPU-Memory-Monitoring und Logging
  - Optimierte Tensor-Freigabe und Cache-Management
  - Setzen von GPU-Memory-Limits für bessere Stabilität

### Technische Details
- Neue `_monitor_gpu_memory()` Methode für detaillierte GPU-Metriken
- Verbesserte `_cleanup_gpu_memory()` Methode mit intelligenten Cleanup-Strategien
- Optimierte Batch-Größenanpassung mit automatischer Reaktion auf Speicherprobleme
- Implementierung von GPU-Memory-Limits (80% des verfügbaren Speichers)
- Erweiterte Fehlerbehandlung und Logging für GPU-bezogene Probleme

### Performance
- Reduzierte GPU-Memory-Leaks bei langer Laufzeit
- Verbesserte Stabilität bei hoher Last
- Optimierte Batch-Verarbeitung basierend auf verfügbarem GPU-Speicher

## [1.2.0] - 2024-03-22

### Hinzugefügt
- Neue FileStatusManager-Klasse für effizientes Status-Management
- Paginierung für große Datensätze
- Erweiterte Filter- und Sortierfunktionen
- Status-Zusammenfassung mit Metriken
- Optimierte UI-Komponenten für bessere Performance
- Asynchrone Status-Updates
- Lazy Loading für Dateilisten

### Geändert
- Überarbeitete UI-Struktur für bessere Übersichtlichkeit
- Optimierte Datenstruktur für Dateistatus
- Verbesserte State-Management-Implementierung
- Effizientere Speichernutzung

### Performance
- Reduzierte UI-Last bei großen Datensätzen
- Schnellere initiale Ladezeit
- Optimierte Speichernutzung
- Verbesserte Reaktionszeit bei Status-Updates

## [1.2.1] - 2024-03-22

### Hinzugefügt
- Detaillierte Systemanforderungen für verschiedene Deployment-Szenarien
  - Spezifikationen für Server mit lokaler GPU
    - Minimale Anforderungen: 4 Cores, 16GB RAM, RTX 2060
    - Empfohlene Anforderungen: 8 Cores, 32GB RAM, RTX 3080
  - Anforderungen für Remote GPU-Implementierungen
    - Minimale Anforderungen: 2 Cores, 8GB RAM, T4 GPU
    - Empfohlene Anforderungen: 4 Cores, 16GB RAM, A100 GPU
  - Performance-Erwartungen für beide Szenarien
    - Lokale GPU: ~100ms pro Frame, 4-8 Frames parallel
    - Remote GPU: ~150-200ms pro Frame, 2-4 Frames parallel
  - Skalierungsoptionen dokumentiert
    - Horizontale Skalierung mit Load Balancing
    - Vertikale Skalierung durch Hardware-Upgrades
  - Erweiterte Monitoring-Anforderungen
    - GPU-Memory-Monitoring
    - Netzwerk-Performance
    - Remote GPU-Verfügbarkeit

### Geändert
- Angepasste Performance-Erwartungen für Remote GPU
  - Reduzierte Batch-Größen (2-4 statt 4-8)
  - Erhöhte Latenz toleranz (<100ms)
  - Optimierte Memory-Nutzung (~3GB pro Service)
- Optimierte Netzwerkanforderungen
  - Minimale Bandbreite: 100Mbps
  - Empfohlene Bandbreite: 1Gbps
  - Latenz-Anforderungen: <100ms
- Erweiterte Monitoring-Kriterien
  - UI-Performance-Metriken
  - Status-Update-Latenz
  - Remote GPU-Verfügbarkeit

### Dokumentation
- Neue Sektion für Systemanforderungen in STATUS.md
  - Detaillierte Hardware-Spezifikationen
  - Performance-Benchmarks für verschiedene Konfigurationen
  - Skalierungsrichtlinien
- Aktualisierte Deployment-Guides
  - Lokale GPU-Installation
  - Remote GPU-Konfiguration
  - Hybrid-Deployment-Optionen

### Performance
- Lokale GPU
  - Verarbeitungszeit: ~100ms pro Frame
  - Batch-Größe: 4-8 Frames
  - GPU-Auslastung: 70-80%
  - UI-Performance: >1000 Dateien
- Remote GPU
  - Verarbeitungszeit: ~150-200ms pro Frame
  - Batch-Größe: 2-4 Frames
  - GPU-Auslastung: 60-70%
  - UI-Performance: >500 Dateien

## [1.2.2] - 2024-03-22

### Dokumentation
- Detaillierte Dokumentation der in Bearbeitung befindlichen Features
  - Erweiterte Fehlerbehandlung
    - Zentrales Error-Handling-System
    - Automatische Fehlerklassifizierung
    - Kontextbasierte Fehlerbehandlung
  - Verbesserte Logging-Implementierung
    - Strukturiertes Logging
    - Log-Rotation und -Archivierung
    - Performance-Metriken
  - Erweiterte Cloud-Integration
    - Optimierte Upload/Download-Strategien
    - Automatische Retry-Mechanismen
    - Progress-Tracking
  - UI-Optimierungen
    - Erweiterte Filter und Sortierung
    - Verbesserte Dateivorschau
    - Responsive Design

## [1.2.3] - 2024-03-22

### Hinzugefügt
- Erweiterte Fehlerbehandlung
  - Zentrales Error-Handling-System mit `ErrorHandler`-Klasse
  - Kategorisierung von Fehlern nach Schweregrad und Typ
  - Kontextbasierte Fehlerbehandlung
  - Automatische Fehlerberichterstattung

- Verbesserte Logging-Implementierung
  - Strukturiertes Logging mit JSON-Format
  - Log-Rotation und -Archivierung
  - Performance-Metriken im Logging
  - Zentralisierte Log-Aggregation

- Erweiterte Cloud-Integration
  - Multi-Cloud-Support (AWS, GCP, Azure, Dropbox, MEGA)
  - Optimierte Upload/Download-Strategien
  - Automatische Retry-Mechanismen
  - Progress-Tracking für Cloud-Operationen
  - Bandbreitenoptimierung

### Geändert
- Verbesserte Fehlerbehandlung in der UI
- Optimierte Cloud-Storage-Operationen
- Erweiterte Logging-Funktionalität

### Performance
- Reduzierte Latenz bei Cloud-Operationen
- Optimierte Speichernutzung
- Verbesserte Fehlerbehandlung

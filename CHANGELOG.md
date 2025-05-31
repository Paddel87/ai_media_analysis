# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt der [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2024-03-20
### Hinzugefügt
- Versionssystem implementiert
- Strukturierte Dokumentation in STATUS.md, CHANGELOG.md und README.md
- Verbesserte Projektübersicht

### Geändert
- Dokumentation aktualisiert
- Versionsnummern in allen relevanten Dateien synchronisiert

## [0.2.0] - 2024-03-19
### Hinzugefügt
- Manuelle Job-Steuerung implementiert
- Job-Manager API mit FastAPI
- Batch-Management-System
- GPU-Provider Interface (Vast.ai, RunPod)
- Umgebungsvariablen-Konfiguration
- Setup-Skripte für .env-Datei

### Geändert
- Standardmäßig deaktivierte automatische Job-Verarbeitung
- Verbesserte Docker-Compose-Konfiguration
- Aktualisierte Dokumentation

### Behoben
- GPU-Instanz-Management optimiert
- Fehlerbehandlung verbessert

## [0.1.0] - 2024-03-18
### Hinzugefügt
- Initiale Projektstruktur
- Basis-Docker-Konfiguration
- README.md mit Projektbeschreibung

## [0.4.0] - 2024-03-20
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

### Pending
- GPU runtime validation
- Inter-service signaling via Redis (jobs, results, scaling triggers)
- Shared logging and healthchecks

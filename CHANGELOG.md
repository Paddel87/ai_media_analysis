# Changelog

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

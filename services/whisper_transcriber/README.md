# Whisper Transkription Service

## Beschreibung
Der Whisper Transkription Service ist ein leistungsstarker Dienst zur Audio-Transkription mit OpenAI Whisper. Er unterstützt verschiedene Sprachen und Modellgrößen für optimale Ergebnisse.

## Features
- Audio-Transkription mit OpenAI Whisper
- Unterstützung für verschiedene Sprachen
- Verschiedene Modellgrößen (tiny bis large)
- GPU-Beschleunigung
- REST API Interface

## Technische Details

### Abhängigkeiten
- FastAPI
- PyTorch
- OpenAI Whisper
- FFmpeg
- NumPy

### API Endpoints

#### POST /transcribe
Transkribiert eine Audiodatei.

**Request Body:**
```json
{
    "job_id": "string",
    "media_id": "string",
    "source_type": "string",
    "language": "string (optional)",
    "model_size": "string (default: base)",
    "task": "string (default: transcribe)"
}
```

**Response:**
```json
{
    "text": "Transkribierter Text",
    "segments": [
        {
            "id": 0,
            "start": 0.0,
            "end": 5.0,
            "text": "Segment Text"
        }
    ],
    "language": "detected_language",
    "job_id": "string",
    "media_id": "string",
    "source_type": "string",
    "timestamp": "ISO8601"
}
```

#### GET /health
Health Check Endpoint.

**Response:**
```json
{
    "status": "healthy",
    "gpu_available": true,
    "model_loaded": true
}
```

## Installation

1. Docker Image bauen:
```bash
docker build -t whisper-transcriber .
```

2. Service starten:
```bash
docker run -d -p 8000:8000 --gpus all whisper-transcriber
```

## Konfiguration

### Umgebungsvariablen
- `WHISPER_MODEL_PATH`: Pfad zu den Whisper-Modellen (Standard: /app/models)
- `PYTHONUNBUFFERED`: Python Output-Buffering deaktivieren

### Modellgrößen
- tiny: ~1GB RAM
- base: ~1GB RAM
- small: ~2GB RAM
- medium: ~5GB RAM
- large: ~10GB RAM

### GPU Support
Der Service nutzt automatisch GPU wenn verfügbar. Für optimale Performance wird eine NVIDIA GPU mit CUDA empfohlen.

## Fehlerbehandlung

Der Service implementiert umfangreiche Fehlerbehandlung:
- Validierung der Eingabedaten
- Exception Handling für alle Operationen
- Logging von Fehlern und Warnungen
- Temporäre Dateiverwaltung

## Performance

- GPU-beschleunigte Inferenz
- Modell-Caching
- Effiziente Audio-Verarbeitung
- Optimierte Speichernutzung

## Sicherheit

- Input-Validierung
- Exception Handling
- Sichere temporäre Dateiverwaltung
- Rate Limiting (konfigurierbar)

## Monitoring

- Health Check Endpoint
- Logging
- GPU-Status
- Modell-Status

## Bekannte Einschränkungen

- Maximale Audiodateigröße: 1GB
- Unterstützte Formate: MP3, WAV, M4A, FLAC
- Maximale Audiolänge: 30 Minuten
- GPU-Speicher abhängig von Modellgröße

## Roadmap

- [ ] Batch-Verarbeitung
- [ ] Streaming-Unterstützung
- [ ] Zusätzliche Audio-Formate
- [ ] Erweiterte Spracherkennung
- [ ] Caching-System
- [ ] Erweiterte Metriken
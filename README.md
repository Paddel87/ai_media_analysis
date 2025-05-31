# AI Media Analysis

Ein fortschrittliches System zur Analyse von Medieninhalten mit Fokus auf Sicherheit und Zustimmung.

## Features

### Restraint Detection
- Erkennung verschiedener Fesselungsarten
- Sicherheitsbewertung und Risikoanalyse
- Zustimmungsanalyse und Kontextbewertung
- Überwachungsstatus und Alleinlassensituationen
- Audio-Analyse für Notfallsituationen

### Performance & Skalierung
- GPU-optimierte Verarbeitung
- Effiziente Batch-Verarbeitung
- Intelligentes Caching-System
- Parallele Modellausführung
- Automatische Skalierung
- Dynamisches Instanz-Management

### Cloud-Integration
- Vast.ai Integration für GPU-Instanzen
- Dynamische Instanzerstellung
- Intelligente Lastverteilung
- Kostenoptimierte Ausführung
- SSH-Management für Remote-Zugriff

## Installation

### Voraussetzungen
- Python 3.8+
- CUDA-kompatible GPU
- Vast.ai API-Key
- SSH-Key für Remote-Zugriff

### Umgebungsvariablen
```bash
VAST_AI_API_KEY=your_api_key
SSH_KEY_PATH=~/.ssh/id_rsa
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### Installation
```bash
pip install -r requirements.txt
```

## Verwendung

### Basis-Analyse
```python
from services.restraint_detection import RestraintDetector

detector = RestraintDetector()
result = await detector.analyze_frame(frame, audio_data, sample_rate)
```

### Batch-Verarbeitung
```python
results = await detector.process_batch(frames, audio_data, sample_rates)
```

### Instanz-Management
```python
# Automatische Skalierung
await detector.instance_manager.scale_instances(current_load)

# Status-Update
await detector.instance_manager.update_instance_status()
```

## Konfiguration

### GPU-Optimierungen
- Batch-Größe: 32
- GPU-Speicher-Schwellenwert: 0.8
- Cache-TTL: 3600 Sekunden
- Frame-Sampling-Rate: 2

### Skalierung
- Maximale Instanzen: 5
- Minimale Auslastung: 0.7
- Maximale Auslastung: 0.9

### Modell-Anforderungen
- CLIP: 6GB GPU-Speicher
- Whisper: 8GB GPU-Speicher

## API-Endpunkte

### Frame-Analyse
```http
POST /analyze/frame
Content-Type: application/json

{
    "frame": [...],
    "audio_data": [...],
    "sample_rate": 44100
}
```

### Batch-Analyse
```http
POST /analyze/batch
Content-Type: application/json

{
    "frames": [[...], [...]],
    "audio_data": [[...], [...]],
    "sample_rates": [44100, 44100]
}
```

## Lizenz

MIT License

## Beitragen

1. Fork erstellen
2. Feature-Branch erstellen
3. Änderungen committen
4. Pull Request erstellen
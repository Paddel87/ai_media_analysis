# Vision Pipeline Service

Der Vision Pipeline Service ist ein leistungsstarker Service zur Analyse von Bildern und Videos mit verschiedenen KI-Modulen. Er koordiniert die Verarbeitung von Medien durch Pose Estimation, OCR und NSFW-Erkennung.

## Features

- Parallele Verarbeitung mehrerer Videos und Bilder
- Optimiertes Batch-Processing für effiziente GPU-Nutzung
- Asynchrone Verarbeitung mit Job-Queue
- Frame-Sampling für effiziente Video-Analyse
- Caching-Strategien für wiederholte Analysen
- Umfangreiche Fehlerbehandlung und Logging

## API-Endpunkte

### Videos analysieren

```http
POST /analyze/videos
```

**Request:**
```json
{
    "video_paths": ["/path/to/video1.mp4", "/path/to/video2.mp4"],
    "batch_size": 4,
    "frame_sampling_rate": 2
}
```

**Response:**
```json
{
    "job_id": "video_20240315_123456",
    "status": "queued",
    "created_at": "2024-03-15T12:34:56"
}
```

### Bilder analysieren

```http
POST /analyze/images
```

**Request:**
```json
{
    "image_paths": ["/path/to/image1.jpg", "/path/to/image2.jpg"],
    "batch_size": 4
}
```

**Response:**
```json
{
    "job_id": "image_20240315_123456",
    "status": "queued",
    "created_at": "2024-03-15T12:34:56"
}
```

### Job-Status abrufen

```http
GET /jobs/{job_id}
```

**Response:**
```json
{
    "job_id": "video_20240315_123456",
    "status": "completed",
    "created_at": "2024-03-15T12:34:56",
    "updated_at": "2024-03-15T12:35:00",
    "result": {
        "output_path": "/path/to/results.json",
        "analysis": {
            "pose": [...],
            "ocr": [...],
            "nsfw": [...]
        }
    }
}
```

### Health-Check

```http
GET /health
```

**Response:**
```json
{
    "status": "healthy",
    "services": {
        "pose_estimation": true,
        "ocr_detection": true,
        "nsfw_detection": true
    }
}
```

## Konfiguration

Der Service kann über Umgebungsvariablen konfiguriert werden:

- `POSE_SERVICE_URL`: URL des Pose Estimation Services
- `OCR_SERVICE_URL`: URL des OCR Detection Services
- `NSFW_SERVICE_URL`: URL des NSFW Detection Services
- `BATCH_SIZE`: Anzahl der Frames/Bilder pro Batch (Standard: 4)
- `FRAME_SAMPLING_RATE`: Jedes n-te Frame wird analysiert (Standard: 2)
- `MAX_WORKERS`: Maximale Anzahl paralleler Worker (Standard: 4)
- `OUTPUT_DIR`: Verzeichnis für Analyseergebnisse
- `REDIS_HOST`: Redis Host (Standard: localhost)
- `REDIS_PORT`: Redis Port (Standard: 6379)

## Installation

### Docker

```bash
# Image bauen
docker build -t ai_media_analysis/vision_pipeline:latest .

# Container starten
docker run -d \
    --name vision_pipeline \
    --gpus all \
    -v /path/to/data:/app/data \
    -e POSE_SERVICE_URL=http://pose_estimation:8000 \
    -e OCR_SERVICE_URL=http://ocr_detection:8000 \
    -e NSFW_SERVICE_URL=http://clip_nsfw:8000 \
    -e BATCH_SIZE=4 \
    -e FRAME_SAMPLING_RATE=2 \
    -e MAX_WORKERS=4 \
    -e REDIS_HOST=redis \
    -e REDIS_PORT=6379 \
    ai_media_analysis/vision_pipeline:latest
```

### Job-Processor

```bash
# Image bauen
docker build -t ai_media_analysis/vision_job_processor:latest -f Dockerfile.job_processor .

# Container starten
docker run -d \
    --name vision_job_processor \
    --gpus all \
    -v /path/to/data:/app/data \
    -e POSE_SERVICE_URL=http://pose_estimation:8000 \
    -e OCR_SERVICE_URL=http://ocr_detection:8000 \
    -e NSFW_SERVICE_URL=http://clip_nsfw:8000 \
    -e BATCH_SIZE=4 \
    -e FRAME_SAMPLING_RATE=2 \
    -e MAX_WORKERS=4 \
    -e REDIS_HOST=redis \
    -e REDIS_PORT=6379 \
    ai_media_analysis/vision_job_processor:latest
```

## Technische Details

- **Framework**: FastAPI
- **Job-Queue**: Redis + RQ
- **GPU-Unterstützung**: CUDA 11.7
- **Performance-Optimierungen**:
  - Batch-Processing für effiziente GPU-Nutzung
  - Frame-Sampling für reduzierte Verarbeitungszeit
  - Asynchrone Verarbeitung mit Job-Queue
  - Caching-Strategien für wiederholte Analysen
  - Parallele Verarbeitung mehrerer Medien

## Performance-Optimierungen

1. **Batch-Verarbeitung**:
   - Frames werden in optimalen Batches gruppiert
   - Gemeinsame GPU-Nutzung über mehrere Videos/Bilder
   - Reduzierte API-Aufrufe durch Batch-Requests

2. **Frame-Sampling**:
   - Nur jedes n-te Frame wird analysiert
   - Konfigurierbare Sampling-Rate
   - Balance zwischen Genauigkeit und Performance

3. **Asynchrone Verarbeitung**:
   - Parallele Ausführung von Pose, OCR und NSFW-Analyse
   - Effiziente Ressourcennutzung
   - Reduzierte Wartezeiten

4. **Caching**:
   - LRU-Cache für wiederholte Frame-Analyse
   - Reduzierte GPU-Belastung
   - Schnellere Verarbeitung ähnlicher Frames

## Architektur

Die Pipeline besteht aus folgenden Komponenten:

1. **Hauptpipeline** (`main.py`):
   - Koordiniert die Verarbeitung von Bildern und Videos
   - Integriert verschiedene KI-Module
   - Speichert Ergebnisse im JSON-Format

2. **Pose Estimation** (`pose.py`):
   - Kommuniziert mit dem Pose Estimation Service
   - Verarbeitet einzelne Frames und Video-Sequenzen
   - Extrahiert Pose-Daten und Konfidenzwerte

3. **OCR Detection** (`ocr.py`):
   - Kommuniziert mit dem OCR Detection Service
   - Erkennt Text in Bildern und Videos
   - Unterstützt Konfidenzfilterung

4. **NSFW Detection** (`nsfw.py`):
   - Kommuniziert mit dem CLIP NSFW Service
   - Erkennt unangemessene Inhalte
   - Unterstützt verschiedene NSFW-Kategorien

## API

### VisionPipeline Klasse

```python
pipeline = VisionPipeline(
    output_dir="/app/data/results",
    pose_service_url="http://pose_estimation:8000",
    ocr_service_url="http://ocr_detection:8000",
    nsfw_service_url="http://clip_nsfw:8000"
)
```

#### Methoden

- `process_video(video_path: str) -> Dict`:
  - Verarbeitet ein Video durch die Pipeline
  - Gibt ein Dictionary mit Frame-Ergebnissen zurück

- `process_image(image_path: str) -> Dict`:
  - Verarbeitet ein einzelnes Bild
  - Gibt ein Dictionary mit Analyseergebnissen zurück

### Ausgabeformat

```json
{
    "video_path": "path/to/video.mp4",
    "fps": 30.0,
    "total_frames": 1000,
    "processing_start": "2024-03-14T12:00:00",
    "frames": [
        {
            "frame_number": 0,
            "timestamp": 0.0,
            "pose_data": {
                "keypoints": [...],
                "confidence": 0.95
            },
            "ocr_data": {
                "results": [
                    {
                        "text": "Erkannter Text",
                        "confidence": 0.85,
                        "bbox": [x1, y1, x2, y2]
                    }
                ]
            },
            "nsfw_data": {
                "results": [
                    {
                        "category": "nude",
                        "confidence": 0.75,
                        "is_nsfw": true
                    }
                ]
            },
            "processing_time": {
                "pose": 0.1,
                "ocr": 0.2,
                "nsfw": 0.3
            }
        }
    ],
    "processing_end": "2024-03-14T12:01:00"
}
```

## Abhängigkeiten

- OpenCV
- NumPy
- FastAPI
- Requests
- Pose Estimation Service
- OCR Detection Service
- CLIP NSFW Service

## Fehlerbehandlung

Die Pipeline implementiert umfangreiche Fehlerbehandlung:
- Überprüfung der Service-Verfügbarkeit
- Validierung von Eingabedateien
- Logging von Verarbeitungsfehlern
- Graceful Degradation bei Service-Ausfällen

## Monitoring

- Logging von Verarbeitungsfortschritt
- Performance-Metriken pro Frame
- Service-Health-Checks
- Verarbeitungszeiten für einzelne Module

## Nächste Schritte

1. Integration weiterer KI-Module
2. Verbesserung der Performance durch Batch-Verarbeitung
3. Implementierung von Caching-Mechanismen
4. Erweiterung der API-Dokumentation 
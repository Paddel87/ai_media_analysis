# OCR Detection Service

Dieser Service implementiert die Texterkennung (OCR) basierend auf EasyOCR mit Unterstützung für Deutsch und Englisch.

## Features

- Texterkennung in Bildern und Videos
- Unterstützung für Deutsch und Englisch
- GPU-Beschleunigung (wenn verfügbar)
- REST API für einfache Integration
- Automatische Spracherkennung
- Konfidenzwerte für erkannten Text

## API-Endpunkte

### POST /analyze
Analysiert ein Bild und gibt die erkannten Texte zurück.

**Request:**
- Content-Type: multipart/form-data
- Body: Bilddatei

**Response:**
```json
{
    "results": [
        {
            "text": "Erkannter Text",
            "confidence": 0.95,
            "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
            "language": "de"
        }
    ],
    "processing_time": 0.5,
    "image_size": {
        "width": 1920,
        "height": 1080
    }
}
```

### GET /health
Health-Check-Endpunkt für Service-Monitoring.

## Installation

1. Docker-Image bauen:
```bash
docker build -t ocr-detection .
```

2. Container starten:
```bash
docker run -d -p 8000:8000 --gpus all ocr-detection
```

## Technische Details

- Basierend auf EasyOCR
- PyTorch-Backend
- CUDA-Unterstützung
- FastAPI für die REST-API
- Pydantic für Datenvalidierung
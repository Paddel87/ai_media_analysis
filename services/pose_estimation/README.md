# Pose Estimation Service

Dieser Service implementiert die Pose Estimation (Körperhaltungserkennung) basierend auf PARE (Pose And Representation Estimation) und MMPose.

## Features

- Erkennung von 17 Körperpunkten (COCO-Format)
- Unterstützung für mehrere Personen im Bild
- GPU-Beschleunigung (wenn verfügbar)
- REST API für einfache Integration

## API-Endpunkte

### POST /analyze
Analysiert ein Bild und gibt die erkannten Körperhaltungen zurück.

**Request:**
- Content-Type: multipart/form-data
- Body: Bilddatei

**Response:**
```json
{
    "keypoints": [[[x1, y1], [x2, y2], ...]],  // Koordinaten für jede Person
    "scores": [[s1, s2, ...]],                  // Konfidenzwerte für jeden Punkt
    "num_people": N                             // Anzahl erkannte Personen
}
```

### GET /health
Health-Check-Endpunkt für Service-Monitoring.

## Installation

1. Docker-Image bauen:
```bash
docker build -t pose-estimation .
```

2. Container starten:
```bash
docker run -d -p 8000:8000 --gpus all pose-estimation
```

## Technische Details

- Basierend auf HRNet-W48
- COCO-Keypoint-Dataset
- Top-down Pose Estimation
- PyTorch-Backend
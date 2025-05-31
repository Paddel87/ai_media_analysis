# CLIP NSFW Detection Service

Ein Service zur Erkennung von NSFW-Inhalten in Bildern und Videos mit CLIP (Contrastive Language-Image Pre-Training).

## Features

- NSFW-Erkennung mit CLIP ViT-B/32
- GPU-Beschleunigung
- Batch-Verarbeitung
- REST API
- Konfidenzwerte für verschiedene Kategorien

## API Endpoints

### POST /analyze
Analysiert ein einzelnes Bild.

**Request:**
- `file`: Bilddatei (multipart/form-data)

**Response:**
```json
{
    "results": [
        {
            "category": "nude",
            "confidence": 0.85,
            "is_nsfw": true
        },
        {
            "category": "safe",
            "confidence": 0.15,
            "is_nsfw": false
        }
    ],
    "processing_time": 0.1,
    "device": "cuda"
}
```

### POST /batch_analyze
Analysiert mehrere Bilder in einem Batch.

**Request:**
- `files`: Liste von Bilddateien (multipart/form-data)

**Response:**
Liste von Analyseergebnissen pro Bild.

### GET /health
Überprüft den Service-Status.

**Response:**
```json
{
    "status": "healthy",
    "gpu_available": true,
    "device": "cuda"
}
```

## Installation

1. Docker-Image bauen:
```bash
docker build -t clip-nsfw .
```

2. Container starten:
```bash
docker run -d \
    --name clip-nsfw \
    --gpus all \
    -p 8000:8000 \
    clip-nsfw
```

## GPU-Anforderungen

- NVIDIA GPU mit CUDA-Unterstützung
- Mindestens 4GB GPU-Speicher
- CUDA 11.7 oder höher
- cuDNN 8 oder höher

## Konfiguration

Die folgenden Umgebungsvariablen können konfiguriert werden:

- `CUDA_VISIBLE_DEVICES`: GPU-Geräte-ID (Standard: 0)
- `MODEL_SIZE`: CLIP-Modellgröße (Standard: ViT-B/32)
- `BATCH_SIZE`: Batch-Größe für Verarbeitung (Standard: 1)

## Technische Details

- **Modell**: CLIP ViT-B/32
- **Framework**: PyTorch
- **API**: FastAPI
- **Container**: Docker mit NVIDIA Container Toolkit
- **Sprache**: Python 3.8+

## Nächste Schritte

1. Implementierung von Caching
2. Optimierung der Batch-Verarbeitung
3. Erweiterung der Kategorien
4. Integration in die Vision Pipeline
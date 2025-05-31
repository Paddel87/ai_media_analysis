# AI Media Analysis

**Version:** 0.4.0 (31. Mai 2025)

A modular, fully open-source AI pipeline for automated analysis of videos and image series. Designed for sensitive content filtering, structured metadata generation, and human-in-the-loop refinement.

## 🚀 Features

- 🔎 Person detection, tracking & ReID (face and body)
- 🧠 Action recognition, emotion detection, pose estimation
- 👕 Clothing & body description (optional)
- 🎙 Speech-to-text transcription (Whisper), including translation
- 🚫 NSFW detection and content classification
- 🧾 OCR for watermark/logo/title extraction
- 🧍 Manual object labeling with review UI
- 📁 Supports both videos and sequential image folders
- 📊 LLM-based summarization & tagging
- 🧠 Continual learning with manual feedback
- 🧩 Fully modular via Docker microservices
- 🧘 On-demand GPU usage via Vast.ai or RunPod (autoscaling)
- 🧱 Minimal base system (Netcup VPS) for orchestration and UI

## 📦 Architecture Overview

```mermaid
flowchart LR
    A[Media Input] --> B[Keyframe Sampling / Sorting]
    B --> C[Vision Services (Dockerized)]
    C --> D[Metadata Collector]
    D --> E[Vector DB (Qdrant)]
    D --> F[chunk-meta.json]
    F --> G[LLM Summarization (API)]
    G --> H[Safety Check → Fallback LLM if needed]
    H --> I[Streamlit Review UI]
```

## 🗂 Directory Structure

ai_media_analysis/
├── .env.example              # Environment variable template
├── docker-compose.yml        # Docker stack for media services
├── setup/                    # Deployment and folder setup scripts
├── services/                 # Modular microservices
│   ├── control/              # Scheduler, Watchdog
│   ├── ui/                   # Streamlit review interface
│   ├── vector_db/            # Qdrant vector database config
│   ├── object_review/        # Manual labeling logic
│   ├── pose_estimation/      # Pose detection and analysis
│   └── vision_pipeline/      # Detection, embedding, NSFW, etc.
├── data_schema/              # JSON schema definitions
└── docs/                     # Architecture notes and instructions

## ⚙ Requirements

    Host: Linux VPS with at least 4 vCPU, 8 GB RAM, 100+ GB SSD
    Python ≥ 3.10
    Docker + Docker Compose
    Optional GPU Node via Vast.ai / RunPod
    Optional: OpenInterpreter for AI-assisted deployment

## 🧪 Status

This project is under active development. Current focus is on implementing and integrating AI modules, starting with Pose Estimation.

## 📜 License

MIT — All components are fully open-source. Only optional LLM APIs (e.g. Gemini, Claude, Llama-3) may involve costs.

## 🧠 AI Architecture

The pipeline follows a modular, GPU-on-demand structure:

- **Ingest Module:** Scene detection and key-frame extraction (FFmpeg, PySceneDetect)
- **Vision Pipeline:** 
  - YOLOv9 for object detection
  - DeepSORT for tracking
  - Face and body ReID (SCRFD, ArcFace, OSNet)
  - Pose estimation (PARE), action recognition (MMAction2), emotion detection (DeepFace)
  - OCR for logos/titles, NSFW classification
  - Whisper for speech-to-text
- **Storage:**
  - Qdrant for vector embeddings
  - Metadata stored in structured JSON files
- **LLM Processing:**
  - Summarization and safety-checks via Gemini, OpenAI, or Claude (via OpenRouter)
- **Manual Review:**
  - Streamlit-based UI for data inspection, merging, feedback, and training

Each component runs in its own Docker container, orchestrated from a central control node.

## Job-Management

Das System unterstützt sowohl automatische als auch manuelle Job-Verarbeitung. Standardmäßig ist die automatische Verarbeitung deaktiviert, sodass Jobs nur manuell durch den Operator gestartet werden können.

### API-Endpunkte

Der Job-Manager bietet folgende API-Endpunkte:

#### Batch-Erstellung
```http
POST /batches
{
  "job_ids": ["job1", "job2", "job3"],
  "batch_name": "mein_batch"
}
```

#### Batch-Start
```http
POST /batches/{batch_id}/start
```

#### Batch-Informationen
```http
GET /batches/{batch_id}
```

#### Batch-Liste
```http
GET /batches
```

#### Wartende Jobs
```http
GET /jobs/pending
```

#### Auto-Process-Einstellung
```http
GET /settings/auto-process
POST /settings/auto-process?enabled=true
```

### Umgebungsvariablen

Die folgenden Umgebungsvariablen können konfiguriert werden:

- `REDIS_HOST`: Redis-Host (Standard: redis)
- `REDIS_PORT`: Redis-Port (Standard: 6379)
- `BATCH_THRESHOLD_HOURS`: Maximale Batch-Dauer in Stunden (Standard: 4)
- `MIN_JOBS_PER_BATCH`: Minimale Anzahl von Jobs pro Batch (Standard: 3)
- `AUTO_PROCESS_JOBS`: Automatische Job-Verarbeitung aktivieren (Standard: false)
- `VAST_API_KEY`: API-Key für Vast.ai
- `RUNPOD_API_KEY`: API-Key für RunPod

### Installation

1. Repository klonen
2. Umgebungsvariablen konfigurieren (siehe `.env.example`)
3. Docker Compose starten:
   ```bash
   docker-compose up -d
   ```

### Verwendung

1. Medien in das `data/incoming`-Verzeichnis hochladen
2. Jobs werden automatisch erkannt und in der Warteschlange gespeichert
3. Über die API können Batches erstellt und gestartet werden
4. GPU-Instanzen werden automatisch erstellt und nach Abschluss gelöscht

### GPU-Provider

Das System unterstützt derzeit folgende GPU-Provider:

- Vast.ai
- RunPod (in Entwicklung)

### Batch-Verarbeitung

- Jobs werden nach Typ (Video/Bild) gruppiert
- Batches werden optimiert nach geschätzter Verarbeitungsdauer
- GPU-Instanzen werden automatisch erstellt und verwaltet
- Nach Abschluss werden alle temporären Dateien bereinigt

### Fehlerbehandlung

- Automatische Wiederholungsversuche bei GPU-Fehlern
- Detaillierte Logging-Informationen
- Status-Updates über die API

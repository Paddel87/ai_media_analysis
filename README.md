# AI Media Analysis

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

🗂 Directory Structure

ai_media_analysis/
├── .env.example              # Environment variable template
├── docker-compose.yml        # Docker stack for media services
├── setup/                    # Deployment and folder setup scripts
├── services/                 # Modular microservices
│   ├── control/              # Scheduler, Watchdog
│   ├── ui/                   # Streamlit review interface
│   ├── vector_db/            # Qdrant vector database config
│   ├── object_review/        # Manual labeling logic
│   └── vision_pipeline/      # Detection, embedding, NSFW, etc.
├── data_schema/              # JSON schema definitions
└── docs/                     # Architecture notes and instructions
⚙ Requirements

    Host: Linux VPS with at least 4 vCPU, 8 GB RAM, 100+ GB SSD

    Python ≥ 3.10

    Docker + Docker Compose

    Optional GPU Node via Vast.ai / RunPod

    Optional: OpenInterpreter for AI-assisted deployment

🧪 Status

This project is under active development. First prototype deployment scripts and LLM prompt logic are in progress.
📜 License

MIT — All components are fully open-source. Only optional LLM APIs (e.g. Gemini, Claude, Llama-3) may involve costs.



## 🧠 AI Architecture

The pipeline follows a modular, GPU-on-demand structure:

1. **Ingest:** Scene detection and frame extraction
2. **Vision Pipeline:** Person detection, ReID, action/emotion/pose recognition, OCR for titles/logos
3. **Vector Storage & Metadata:** Qdrant for embeddings, JSONs for structured metadata
4. **LLM Layer:** Gemini / OpenAI / Claude via OpenRouter for summarization & safety-checks
5. **UI Tools:** Streamlit-based interface for review, labeling and feedback

All services are containerized. GPU nodes are activated on demand using control logic from the `control` module.

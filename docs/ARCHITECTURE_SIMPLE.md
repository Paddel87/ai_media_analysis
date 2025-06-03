# AI Media Analysis - Vereinfachte Architektur

## System-Übersicht

```mermaid
graph TB
    subgraph "🌐 Frontend"
        UI[Streamlit UI]
        Gateway[Nginx Gateway]
    end

    subgraph "🎛️ Control Layer"
        Control[Control Service]
        JobManager[Job Manager]
    end

    subgraph "🧠 AI Services"
        Vision[Vision AI<br/>NSFW, Face, OCR]
        Audio[Audio AI<br/>Whisper, Analysis]
        Analysis[Data Analysis<br/>Dossiers, Vector DB]
    end

    subgraph "💾 Data Layer"
        Redis[(Redis Cache)]
        Files[(File Storage)]
    end

    subgraph "☁️ Cloud"
        CloudGPU[GPU Instances<br/>Vast.ai / RunPod]
    end

    UI --> Gateway
    Gateway --> Control
    Control --> JobManager

    JobManager --> Vision
    JobManager --> Audio
    JobManager --> Analysis
    JobManager --> CloudGPU

    Vision --> Redis
    Audio --> Redis
    Analysis --> Redis

    Vision --> Files
    Audio --> Files
    Analysis --> Files

    classDef frontend fill:#e1f5fe
    classDef control fill:#f3e5f5
    classDef ai fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef cloud fill:#fce4ec

    class UI,Gateway frontend
    class Control,JobManager control
    class Vision,Audio,Analysis ai
    class Redis,Files data
    class CloudGPU cloud
```

## Datenfluss

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Control
    participant JobMgr as Job Manager
    participant AI as AI Services
    participant Cloud
    participant Data

    User->>UI: Upload Media
    UI->>Control: Analyze Request
    Control->>JobMgr: Create Job

    alt GPU Required
        JobMgr->>Cloud: Scale Instance
    end

    JobMgr->>AI: Process Media
    AI->>Data: Store Results

    AI->>JobMgr: Complete
    JobMgr->>Control: Results
    Control->>UI: Analysis
    UI->>User: Display
```

## Service-Ports

| Service | Port | Beschreibung |
|---------|------|-------------|
| Nginx Gateway | 80/443 | HTTP/HTTPS Entry Point |
| Streamlit UI | 8501 | User Interface |
| Whisper | 8001 | Audio Transcription |
| Vector DB | 8002 | Embeddings Storage |
| Pose Estimation | 8003 | Body Analysis |
| Redis | 6379 | Cache & Message Bus |

## Resource-Verteilung

```mermaid
pie title CPU/Memory Allocation
    "Vision AI" : 35
    "Audio AI" : 25
    "Control" : 15
    "Data" : 15
    "UI" : 10
```

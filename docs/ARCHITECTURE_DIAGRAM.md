# AI Media Analysis System - Architektur-Diagramm

## System-Übersicht

Das AI Media Analysis System basiert auf einer **4-Schichten-Mikroservice-Architektur** mit Cloud-GPU-Integration für kostenoptimierte KI-Verarbeitung.

## Hauptarchitektur-Diagramm

```mermaid
graph TB
    subgraph "🌐 External Layer"
        UI[Streamlit UI<br/>:8501]
        API_Gateway[Nginx Gateway<br/>:80/443]
        Cloud_GPU[☁️ Cloud GPU<br/>Vast.ai/RunPod]
    end

    subgraph "🎛️ Layer 4: Orchestrierung & Control"
        Control[Control Service<br/>System-Steuerung]
        JobMgr[Job Manager<br/>Batch-Processing]
        DataPers[Data Persistence<br/>File Management]
    end

    subgraph "🧠 Layer 3: AI Processing Services"
        subgraph "👁️ Vision Services"
            CLIP_NSFW[CLIP NSFW<br/>Content Moderation]
            FaceReID[Face ReID<br/>Gesichtserkennung]
            OCR[OCR Detection<br/>Texterkennung]
            PoseEst[Pose Estimation<br/>Körperhaltung]
            Restraint[Restraint Detection<br/>Objekterkennung]
        end

        subgraph "🎵 Audio Services"
            Whisper[Whisper Transcriber<br/>:8001]
            AudioAnalysis[Audio Analysis<br/>Notfall-Erkennung]
        end

        subgraph "📊 Analysis Services"
            VectorDB[Vector DB<br/>:8002<br/>Embeddings]
            PersonDossier[Person Dossier<br/>Tracking]
            LLM[LLM Service<br/>Zusammenfassung]
        end
    end

    subgraph "💾 Layer 2: Data & Cache Layer"
        Redis[(Redis Cache<br/>:6379<br/>Message Bus)]
        FileSystem[(File System<br/>/data Structure)]
    end

    subgraph "🔧 Layer 1: Infrastructure"
        Network[ai_network<br/>Docker Network]
        HealthChecks[Health Check System]
        Logging[Centralized Logging]
    end

    %% External Connections
    UI --> API_Gateway
    API_Gateway --> Control

    %% Control Flow
    Control --> JobMgr
    Control --> DataPers
    JobMgr --> Cloud_GPU

    %% Processing Dependencies
    JobMgr -.-> CLIP_NSFW
    JobMgr -.-> FaceReID
    JobMgr -.-> OCR
    JobMgr -.-> PoseEst
    JobMgr -.-> Restraint
    JobMgr -.-> Whisper
    JobMgr -.-> AudioAnalysis

    %% Data Flow
    CLIP_NSFW --> VectorDB
    FaceReID --> PersonDossier
    OCR --> VectorDB
    PoseEst --> VectorDB
    Restraint --> PersonDossier
    Whisper --> LLM
    AudioAnalysis --> PersonDossier

    %% All Services connect to Redis
    Control --- Redis
    JobMgr --- Redis
    DataPers --- Redis
    CLIP_NSFW --- Redis
    FaceReID --- Redis
    OCR --- Redis
    PoseEst --- Redis
    Restraint --- Redis
    Whisper --- Redis
    AudioAnalysis --- Redis
    VectorDB --- Redis
    PersonDossier --- Redis
    LLM --- Redis

    %% File System Access
    DataPers --- FileSystem
    VectorDB --- FileSystem
    PersonDossier --- FileSystem

    %% Infrastructure
    Network -.-> HealthChecks
    HealthChecks -.-> Logging

    classDef external fill:#e1f5fe
    classDef control fill:#f3e5f5
    classDef vision fill:#e8f5e8
    classDef audio fill:#fff3e0
    classDef analysis fill:#fce4ec
    classDef data fill:#f1f8e9
    classDef infra fill:#f5f5f5

    class UI,API_Gateway,Cloud_GPU external
    class Control,JobMgr,DataPers control
    class CLIP_NSFW,FaceReID,OCR,PoseEst,Restraint vision
    class Whisper,AudioAnalysis audio
    class VectorDB,PersonDossier,LLM analysis
    class Redis,FileSystem data
    class Network,HealthChecks,Logging infra
```

## Datenfluss-Diagramm

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant UI as 🖥️ Streamlit UI
    participant Control as 🎛️ Control Service
    participant JobMgr as ⚙️ Job Manager
    participant Redis as 💾 Redis
    participant Vision as 👁️ Vision Services
    participant Audio as 🎵 Audio Services
    participant Dossier as 📋 Person Dossier
    participant Cloud as ☁️ Cloud GPU

    User->>UI: Upload Media
    UI->>Control: POST /analyze
    Control->>JobMgr: Create Job
    JobMgr->>Redis: Queue Job

    alt GPU-intensive Task
        JobMgr->>Cloud: Scale GPU Instance
        Cloud-->>JobMgr: Instance Ready
    end

    par Vision Processing
        JobMgr->>Vision: Process Images
        Vision->>Redis: Cache Results
        Vision->>Dossier: Update Person Data
    and Audio Processing
        JobMgr->>Audio: Process Audio
        Audio->>Redis: Cache Transcription
        Audio->>Dossier: Update Audio Data
    end

    Dossier->>Redis: Store Updated Dossier
    JobMgr->>Control: Job Complete
    Control->>UI: Analysis Results
    UI->>User: Display Results

    opt Cleanup
        JobMgr->>Cloud: Destroy GPU Instance
    end
```

## Service-Abhängigkeits-Matrix

```mermaid
graph LR
    subgraph "🔄 Dependency Matrix"
        subgraph "Core Dependencies"
            Redis_Core[Redis<br/>★★★★★]
            Network_Core[Docker Network<br/>★★★★★]
            Health_Core[Health Checks<br/>★★★★★]
        end

        subgraph "Service Dependencies"
            JobMgr_Dep[Job Manager<br/>→ Redis, Cloud APIs]
            Control_Dep[Control<br/>→ Redis, All Services]
            Vision_Dep[Vision Services<br/>→ Redis, File System]
            Audio_Dep[Audio Services<br/>→ Redis, Models]
            Data_Dep[Data Services<br/>→ Redis, File System]
        end

        subgraph "External Dependencies"
            CloudGPU_Dep[Cloud GPU<br/>→ Vast.ai, RunPod]
            UI_Dep[UI<br/>→ Nginx, APIs]
            Models_Dep[AI Models<br/>→ HuggingFace, OpenAI]
        end
    end

    classDef critical fill:#ffcdd2
    classDef important fill:#fff3e0
    classDef optional fill:#e8f5e8

    class Redis_Core,Network_Core,Health_Core critical
    class JobMgr_Dep,Control_Dep,Vision_Dep,Audio_Dep,Data_Dep important
    class CloudGPU_Dep,UI_Dep,Models_Dep optional
```

## Resource-Allocation-Diagramm

```mermaid
pie title Resource-Verteilung (CPU/Memory)
    "Control Services (15%)" : 15
    "Vision AI (35%)" : 35
    "Audio AI (25%)" : 25
    "Data & Redis (15%)" : 15
    "UI & Gateway (10%)" : 10
```

## Cloud-Integration-Architektur

```mermaid
graph TB
    subgraph "🏠 VPS Infrastructure (CPU-optimiert)"
        VPS_Control[Control Services]
        VPS_Data[Data Management]
        VPS_Cache[Redis Cache]
        VPS_Gateway[Nginx Gateway]
    end

    subgraph "☁️ Cloud GPU (On-Demand)"
        subgraph "Vast.ai Pool"
            Vast_CLIP[CLIP Services]
            Vast_Face[Face Recognition]
            Vast_Whisper[Whisper Models]
        end

        subgraph "RunPod Pool"
            RunPod_Batch[Batch Processing]
            RunPod_Heavy[Heavy Models]
        end

        subgraph "AWS/GCP (Fallback)"
            AWS_Instances[GPU Instances]
            GCP_Instances[TPU Instances]
        end
    end

    subgraph "💰 Cost Optimization Engine"
        PriceMonitor[Price Monitor]
        LoadBalancer[Smart Load Balancer]
        AutoScaler[Auto Scaler]
    end

    VPS_Control --> PriceMonitor
    PriceMonitor --> LoadBalancer
    LoadBalancer --> Vast_CLIP
    LoadBalancer --> RunPod_Batch
    LoadBalancer --> AWS_Instances

    AutoScaler --> Vast_Face
    AutoScaler --> RunPod_Heavy
    AutoScaler --> GCP_Instances

    VPS_Cache <--> Vast_CLIP
    VPS_Cache <--> RunPod_Batch
    VPS_Cache <--> AWS_Instances

    classDef vps fill:#e3f2fd
    classDef cloud fill:#f3e5f5
    classDef cost fill:#fff8e1

    class VPS_Control,VPS_Data,VPS_Cache,VPS_Gateway vps
    class Vast_CLIP,Vast_Face,Vast_Whisper,RunPod_Batch,RunPod_Heavy,AWS_Instances,GCP_Instances cloud
    class PriceMonitor,LoadBalancer,AutoScaler cost
```

## Sicherheits-Architektur

```mermaid
graph TB
    subgraph "🛡️ Security Layers"
        subgraph "Input Validation"
            InputSanitize[Input Sanitization]
            MediaValidation[Media Validation]
            RateLimiting[Rate Limiting]
        end

        subgraph "Content Safety Pipeline"
            NSFW_Check[NSFW Detection]
            Violence_Check[Violence Detection]
            Emergency_Check[Emergency Detection]
            Consent_Check[Consent Assessment]
        end

        subgraph "Data Protection"
            Encryption[Data Encryption]
            AccessControl[Access Control]
            AuditLog[Audit Logging]
            DataRetention[Data Retention]
        end

        subgraph "Compliance Monitoring"
            GDPR_Compliance[GDPR Compliance]
            Ethics_Review[Ethics Review]
            Legal_Safeguards[Legal Safeguards]
            ReportGeneration[Report Generation]
        end
    end

    InputSanitize --> NSFW_Check
    MediaValidation --> Violence_Check
    RateLimiting --> Emergency_Check

    NSFW_Check --> Encryption
    Violence_Check --> AccessControl
    Emergency_Check --> AuditLog
    Consent_Check --> DataRetention

    Encryption --> GDPR_Compliance
    AccessControl --> Ethics_Review
    AuditLog --> Legal_Safeguards
    DataRetention --> ReportGeneration

    classDef input fill:#e8f5e8
    classDef safety fill:#fff3e0
    classDef protection fill:#f3e5f5
    classDef compliance fill:#e1f5fe

    class InputSanitize,MediaValidation,RateLimiting input
    class NSFW_Check,Violence_Check,Emergency_Check,Consent_Check safety
    class Encryption,AccessControl,AuditLog,DataRetention protection
```

## Entwicklungsarchitektur

```mermaid
graph LR
    subgraph "🔧 Development Pipeline"
        Dev[Development]
        Test[Testing]
        Build[Build]
        Deploy[Deploy]
    end

    subgraph "📋 Quality Gates"
        Format[Black Formatting]
        Lint[Linter Compliance]
        Type[Type Checking]
        Security[Security Scan]
    end

    subgraph "🚀 Deployment Stages"
        Local[Local Docker]
        Staging[Staging VPS]
        Production[Production Cloud]
    end

    Dev --> Format
    Format --> Lint
    Lint --> Type
    Type --> Security
    Security --> Test
    Test --> Build
    Build --> Local
    Local --> Staging
    Staging --> Production

    classDef dev fill:#e8f5e8
    classDef quality fill:#fff3e0
    classDef deploy fill:#f3e5f5

    class Dev,Test,Build,Deploy dev
    class Format,Lint,Type,Security quality
    class Local,Staging,Production deploy
```

---

## Architektur-Prinzipien

### 🎯 **Design-Philosophie**
1. **Microservice-First**: Jeder Service ist unabhängig deploybar
2. **Cloud-Native**: Hybrid VPS/Cloud für Kostenoptimierung
3. **Safety-by-Design**: Eingebaute Sicherheits- und Compliance-Checks
4. **Async-Everything**: Vollständig asynchrone Verarbeitung
5. **Resource-Aware**: Intelligente GPU-Nutzung und Auto-Scaling

### 🔄 **Skalierungs-Strategie**
- **Horizontale Skalierung**: Mehrere Service-Instanzen
- **Vertikale Skalierung**: Cloud-GPU für intensive Tasks
- **Cost-Optimization**: Dynamische Instanz-Verwaltung
- **Load-Balancing**: Intelligente Workload-Verteilung

### 🛡️ **Sicherheits-Konzept**
- **Defense-in-Depth**: Mehrschichtige Sicherheit
- **Principle of Least Privilege**: Minimale Berechtigungen
- **Zero-Trust**: Alle Verbindungen werden validiert

### 📊 **Monitoring & Observability**
- **Health-Checks**: Kontinuierliche Service-Überwachung
- **Centralized Logging**: Strukturierte Log-Aggregation
- **Metrics Collection**: Performance und Business-Metriken
- **Alerting**: Proaktive Benachrichtigungen bei Anomalien

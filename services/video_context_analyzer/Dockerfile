# OPTION A PRIMARY: CPU-OPTIMIZED VIDEO CONTEXT ANALYZER SERVICE
# UC-001 LLM-basierte Video-Kontext-Analyse für Enhanced Manual Analysis
# Version: 2.0.0 - CPU-First Strategy + LLM Integration

FROM python:3.11-slim

# OPTION A OPTIMIZATION: UC-001 Video Analysis Labels
LABEL maintainer="Power-User AI Team"
LABEL version="2.0.0"
LABEL strategy="Option-A-Primary"
LABEL service="video_context_analyzer"
LABEL optimization="cpu_performance_llm"
LABEL uc001_component="video_analysis"

# POWER-USER CPU OPTIMIZATION: System packages for video processing
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libgomp1 \
    curl \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-OPTIMIZED: Performance-first dependency installation
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# POWER-USER: Essential directories for UC-001
RUN mkdir -p /app/data/video_analysis && \
    mkdir -p /app/data/context_results && \
    mkdir -p /app/data/llm_cache && \
    mkdir -p /app/logs && \
    mkdir -p /app/config

# DATA SCHEMA INTEGRATION (UC-001 REQUIREMENT)
COPY data_schema ./data_schema

# APPLICATION CODE
COPY main.py .
COPY *.py .

# OPTION A PRIMARY: Video + LLM Performance settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2
ENV NUMBA_THREADING_LAYER=workqueue
ENV OPENCV_CPU_DISABLE=0

# UC-001 VIDEO CONTEXT ANALYZER CONFIGURATION
ENV UC001_ENABLED=true
ENV VIDEO_ANALYSIS=true
ENV LLM_INTEGRATION=true
ENV CONTEXT_GENERATION=true
ENV MOVEMENT_TRACKING=true
ENV EMOTION_ANALYSIS=true
ENV AUDIO_PROCESSING=true

# CPU-FIRST VIDEO PROCESSING
ENV VIDEO_CPU_THREADS=4
ENV FRAME_BATCH_SIZE=16
ENV ANALYSIS_QUEUE_SIZE=100
ENV MEMORY_OPTIMIZATION=true

# LLM OPTIMIZATION (Option A Primary)
ENV LLM_LOCAL_FIRST=true
ENV LLM_CLOUD_OPTIONAL=true
ENV LLM_COST_AWARENESS=true
ENV LLM_RESPONSE_CACHE=true

# POWER-USER CONTROLS
ENV EXPORT_ENABLED=true
ENV DETAILED_LOGGING=true
ENV PERFORMANCE_MONITORING=true
ENV CONTEXT_QUALITY_THRESHOLD=0.8

# HEALTH CHECK for Power-User monitoring
HEALTHCHECK --interval=30s --timeout=15s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "main.py"]

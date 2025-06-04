# OPTION A PRIMARY: CPU-OPTIMIZED CLOTHING ANALYZER SERVICE
# UC-001 Enhanced Manual Analysis - 200+ Kategorie-Kleidungsklassifikation
# Version: 2.0.0 - CPU-First Strategy + CLIP Integration

FROM python:3.11-slim

# OPTION A OPTIMIZATION: UC-001 Clothing Analysis Labels
LABEL maintainer="Power-User AI Team"
LABEL version="2.0.0"
LABEL strategy="Option-A-Primary"
LABEL service="clothing_analyzer"
LABEL optimization="cpu_performance_clip"
LABEL uc001_component="clothing_classification"
LABEL categories="200+"

# POWER-USER CPU OPTIMIZATION: System packages for CLIP + Image Processing
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libgomp1 \
    curl \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    liblcms2-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-OPTIMIZED: Performance-first dependency installation
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# POWER-USER: Essential directories for UC-001 Clothing Analysis
RUN mkdir -p /app/data/clothing_analysis && \
    mkdir -p /app/data/classifications && \
    mkdir -p /app/data/category_cache && \
    mkdir -p /app/models && \
    mkdir -p /app/logs && \
    mkdir -p /app/config

# DATA SCHEMA INTEGRATION (UC-001 REQUIREMENT)
COPY data_schema ./data_schema

# UC-001 CLOTHING CATEGORIES CONFIGURATION
COPY clothing_categories.json ./clothing_categories.json

# APPLICATION CODE
COPY main.py .
COPY *.py .

# OPTION A PRIMARY: CLIP + CPU Performance settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2
ENV NUMBA_THREADING_LAYER=workqueue

# FORCE CPU-ONLY FOR OPTION A PRIMARY
ENV CUDA_VISIBLE_DEVICES=""
ENV TORCH_DEVICE=cpu

# UC-001 CLOTHING ANALYZER CONFIGURATION
ENV UC001_ENABLED=true
ENV CLOTHING_ANALYSIS=true
ENV CATEGORY_COUNT=200
ENV MATERIAL_DETECTION=true
ENV STYLE_CLASSIFICATION=true
ENV DOSSIER_INTEGRATION=true

# CPU-FIRST CLIP PROCESSING
ENV CLIP_CPU_THREADS=4
ENV CLIP_BATCH_SIZE=8
ENV CLIP_MODEL=ViT-B/32
ENV CLASSIFICATION_CACHE=true

# POWER-USER FEATURES
ENV EXPORT_ENABLED=true
ENV DETAILED_CATEGORIZATION=true
ENV CONFIDENCE_THRESHOLD=0.7
ENV CATEGORY_HIERARCHY=true

# CLOUD ENHANCEMENT (OPTIONAL)
ENV CLOUD_CLASSIFICATION_AVAILABLE=true
ENV CLOUD_COST_AWARENESS=true

# HEALTH CHECK for Power-User monitoring
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "main.py"]

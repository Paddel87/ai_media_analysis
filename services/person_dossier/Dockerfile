# OPTION A PRIMARY: CPU-OPTIMIZED PERSON DOSSIER SERVICE
# Power-User-First: Maximale CPU-Performance für Core-Dossier-Management
# Version: 2.0.0 - CPU-First Strategy

FROM python:3.11-slim

# OPTION A OPTIMIZATION: CPU-Performance Labels
LABEL maintainer="Power-User AI Team"
LABEL version="2.0.0"
LABEL strategy="Option-A-Primary"
LABEL service="person_dossier"
LABEL optimization="cpu_performance"

# POWER-USER CPU OPTIMIZATION: System packages
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# CPU-OPTIMIZED: Performance-first dependency installation
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# POWER-USER: Essential directories
RUN mkdir -p /app/data/dossiers && \
    mkdir -p /app/data/corrections && \
    mkdir -p /app/logs && \
    mkdir -p /app/config

# DATA SCHEMA INTEGRATION (UC-001 REQUIREMENT)
COPY data_schema ./data_schema

# APPLICATION CODE
COPY main.py .
COPY *.py .

# OPTION A PRIMARY: Performance settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2
ENV NUMBA_THREADING_LAYER=workqueue

# UC-001 POWER-USER CONFIGURATION
ENV UC001_ENABLED=true
ENV DOSSIER_INTEGRATION=true
ENV USER_CORRECTIONS=true
ENV CPU_PRIMARY=true
ENV PERFORMANCE_MONITORING=true

# HEALTH CHECK for Power-User monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["python", "main.py"]

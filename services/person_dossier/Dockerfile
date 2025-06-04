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
COPY services/person_dossier/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# POWER-USER: Essential directories
RUN mkdir -p /app/data/dossiers && \
    mkdir -p /app/data/corrections && \
    mkdir -p /app/logs && \
    mkdir -p /app/config

# COMMON SERVICES INTEGRATION (Required for insights_service)
COPY services/common ./services/common

# DATA SCHEMA INTEGRATION (UC-001 REQUIREMENT)
COPY services/person_dossier/data_schema ./data_schema
COPY data_schema ./data_schema_root

# APPLICATION CODE
COPY services/person_dossier/main.py .
COPY services/person_dossier/insights_dossier_service.py .
COPY services/person_dossier/*.py .

# OPTION A PRIMARY: Performance settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=2
ENV NUMBA_THREADING_LAYER=workqueue
ENV PYTHONPATH=/app

# UC-001 POWER-USER CONFIGURATION
ENV UC001_ENABLED=true
ENV DOSSIER_INTEGRATION=true
ENV USER_CORRECTIONS=true
ENV CPU_PRIMARY=true
ENV PERFORMANCE_MONITORING=true

# HEALTH CHECK for Power-User monitoring - updated for insights_dossier port
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || curl -f http://localhost:8021/health || exit 1

EXPOSE 8000
EXPOSE 8021

# Default command - can be overridden in docker-compose
CMD ["python", "main.py"]

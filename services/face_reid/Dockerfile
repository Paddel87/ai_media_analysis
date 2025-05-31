# syntax=docker/dockerfile:1.4
FROM python:3.9-slim

WORKDIR /app

# Installiere Build-Tools und Abhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements
COPY requirements.txt .

# Installiere Python-Pakete
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Erstelle Modelle-Verzeichnis
RUN mkdir -p /app/models

# Kopiere Anwendungscode
COPY main.py .

# Setze Umgebungsvariablen
ENV PYTHONUNBUFFERED=1
ENV CLIP_SERVICE_URL=http://clip-service:8000
ENV MODEL_PATH=/app/models

# Exponiere Port
EXPOSE 8000

# Starte den Service
CMD ["python", "main.py"]
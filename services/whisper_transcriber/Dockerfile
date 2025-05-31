# syntax=docker/dockerfile:1.4
FROM python:3.9-slim

WORKDIR /app

# Installiere Build-Tools und Abhängigkeiten
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Kopiere Requirements
COPY requirements.txt .

# Installiere Python-Pakete
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Kopiere Anwendungscode
COPY main.py .

# Setze Umgebungsvariablen
ENV PYTHONUNBUFFERED=1
ENV WHISPER_MODEL_PATH=/app/models

# Erstelle Modelle-Verzeichnis
RUN mkdir -p /app/models

# Exponiere Port
EXPOSE 8000

# Starte den Service
CMD ["python", "main.py"]
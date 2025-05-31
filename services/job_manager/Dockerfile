FROM nvidia/cuda:11.8.0-base-ubuntu22.04

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Verzeichnisstruktur erstellen
RUN mkdir -p /app/data/incoming/videos \
    && mkdir -p /app/data/incoming/images \
    && mkdir -p /app/data/jobs

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1

# Startbefehl
CMD ["python3", "process_batch.py"] 
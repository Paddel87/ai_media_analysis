FROM nvidia/cuda:12.2.0-cudnn8-runtime-ubuntu22.04

# System-Voraussetzungen
RUN apt-get update && \
    apt-get install -y git ffmpeg libgl1 python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Anforderungen kopieren
COPY requirements.txt .

# Python-Abhängigkeiten installieren
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

# Source Code kopieren
COPY . .

# Startbefehl
CMD ["python3", "main.py"]

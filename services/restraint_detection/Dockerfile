FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# System-Pakete installieren
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Port freigeben
EXPOSE 8000

# Service starten
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
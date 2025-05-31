# Basis-Image mit CUDA-Unterstützung
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# System-Pakete installieren
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis setzen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Port freigeben
EXPOSE 8000

# Startbefehl
CMD ["python3", "main.py"] 
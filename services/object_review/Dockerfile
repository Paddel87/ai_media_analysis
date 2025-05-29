FROM python:3.10-slim

# System-Voraussetzungen
RUN apt-get update && \
    apt-get install -y libgl1 && \
    rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis
WORKDIR /app

# Anforderungen kopieren
COPY requirements.txt .

# Python-Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Source Code kopieren
COPY . .

# Startbefehl
CMD ["python", "main.py"]

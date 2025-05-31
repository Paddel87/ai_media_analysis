FROM python:3.10-slim

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Python-Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY . .

# Verzeichnisstruktur erstellen
RUN mkdir -p /app/data/incoming/videos \
    && mkdir -p /app/data/incoming/images

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1

# Startbefehl
CMD ["python", "generator.py"] 
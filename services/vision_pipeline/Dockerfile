FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

# System-Abhängigkeiten
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode
COPY . .

# Verzeichnisse erstellen
RUN mkdir -p /app/data/incoming /app/data/results

# Umgebungsvariablen
ENV PYTHONUNBUFFERED=1

# Startbefehl
CMD ["python", "main.py"]

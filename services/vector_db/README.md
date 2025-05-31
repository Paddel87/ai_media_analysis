# Vector DB Service

## Beschreibung
Der Vector DB Service ist ein leistungsstarker Dienst für die Speicherung und Suche von Vektorembeddings mit Qdrant. Er ermöglicht effiziente Ähnlichkeitssuchen und die Verwaltung von Vektorkollektionen.

## Features
- Vektorspeicherung und -suche mit Qdrant
- Collection-Management
- Ähnlichkeitssuche mit verschiedenen Metriken
- REST API Interface
- Skalierbare Architektur

## Technische Details

### Abhängigkeiten
- FastAPI
- Qdrant Client
- NumPy
- Pydantic

### API Endpoints

#### POST /collections
Erstellt eine neue Collection.

**Request Body:**
```json
{
    "name": "collection_name",
    "vector_size": 768,
    "distance": "Cosine"
}
```

**Response:**
```json
{
    "success": true
}
```

#### POST /vectors
Speichert oder aktualisiert einen Vektor.

**Request Body:**
```json
{
    "id": "vector_id",
    "vector": [0.1, 0.2, ...],
    "metadata": {
        "text": "Beispieltext",
        "source": "document1"
    },
    "collection": "collection_name"
}
```

**Response:**
```json
{
    "success": true
}
```

#### POST /search
Sucht ähnliche Vektoren.

**Request Body:**
```json
{
    "vector": [0.1, 0.2, ...],
    "collection": "collection_name",
    "limit": 10,
    "score_threshold": 0.7,
    "filter": {
        "must": [
            {
                "key": "source",
                "match": {
                    "value": "document1"
                }
            }
        ]
    }
}
```

**Response:**
```json
{
    "results": [
        {
            "id": "vector_id",
            "score": 0.85,
            "metadata": {
                "text": "Beispieltext",
                "source": "document1"
            }
        }
    ]
}
```

#### DELETE /vectors/{collection}/{vector_id}
Löscht einen Vektor.

**Response:**
```json
{
    "success": true
}
```

#### GET /health
Health Check Endpoint.

**Response:**
```json
{
    "status": "healthy",
    "collections": 5,
    "qdrant_connected": true
}
```

## Installation

1. Docker Image bauen:
```bash
docker build -t vector-db-service .
```

2. Service starten:
```bash
docker run -d -p 8000:8000 vector-db-service
```

## Konfiguration

### Umgebungsvariablen
- `QDRANT_HOST`: Host des Qdrant-Servers (Standard: localhost)
- `QDRANT_PORT`: Port des Qdrant-Servers (Standard: 6333)
- `PYTHONUNBUFFERED`: Python Output-Buffering deaktivieren

### Qdrant Server
Der Service benötigt einen laufenden Qdrant-Server. Dieser kann als separater Container gestartet werden:

```bash
docker run -d -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

## Fehlerbehandlung

Der Service implementiert umfangreiche Fehlerbehandlung:
- Validierung der Eingabedaten
- Exception Handling für alle Operationen
- Logging von Fehlern und Warnungen
- Health Checks für Qdrant-Verbindung

## Performance

- Effiziente Vektorsuche
- Batch-Operationen
- Optimierte Speichernutzung
- Skalierbare Architektur

## Sicherheit

- Input-Validierung
- Exception Handling
- Rate Limiting (konfigurierbar)
- Secure Headers

## Monitoring

- Health Check Endpoint
- Logging
- Collection-Status
- Qdrant-Verbindungsstatus

## Bekannte Einschränkungen

- Maximale Vektorgröße: 2048 Dimensionen
- Maximale Collection-Größe: Abhängig von verfügbarem RAM
- Maximale Batch-Größe: 100 Vektoren

## Roadmap

- [ ] Batch-Operationen optimieren
- [ ] Zusätzliche Distanzmetriken
- [ ] Erweiterte Filteroptionen
- [ ] Caching-System
- [ ] Erweiterte Metriken
- [ ] Backup-System 
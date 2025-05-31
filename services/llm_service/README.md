# LLM Service

## Beschreibung
Der LLM Service ist ein leistungsstarker Dienst für Textgenerierung und Embeddings mit verschiedenen LLM-Modellen (OpenAI GPT-4, Anthropic Claude, Google Gemini), Vector DB Integration und Media Service Integration.

## Features
- Textgenerierung mit verschiedenen LLMs
- Embedding-Erstellung
- Vector DB Integration für semantische Suche
- Media Service Integration für Medienanalyse
- Safety Settings für Gemini
- Kontextunterstützung
- System Prompts
- REST API Interface

## Technische Details

### Abhängigkeiten
- FastAPI
- OpenAI
- Anthropic
- Google Generative AI
- NumPy
- Pydantic
- Requests (für Service Integrationen)

### API Endpoints

#### POST /generate
Generiert Text mit dem ausgewählten LLM.

**Request Body:**
```json
{
    "prompt": "string",
    "model": "string",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "string (optional)",
    "context": [
        {
            "role": "string",
            "content": "string"
        }
    ],
    "safety_settings": {
        "harassment": "string",
        "hate_speech": "string",
        "sexually_explicit": "string",
        "dangerous_content": "string",
        "disabled": false
    }
}
```

**Verfügbare Modelle:**
- OpenAI: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Anthropic: `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Gemini: `gemini-pro`, `gemini-pro-vision`

**Safety Settings (nur Gemini):**
- `block_none`: Keine Einschränkungen
- `block_low_and_above`: Blockiert niedrige und höhere Risiken
- `block_medium_and_above`: Blockiert mittlere und höhere Risiken
- `block_high_and_above`: Blockiert nur hohe Risiken
- `disabled`: Deaktiviert alle Safety Settings

**Response:**
```json
{
    "text": "string",
    "model": "string",
    "usage": {
        "total_tokens": 0
    },
    "finish_reason": "string",
    "safety_ratings": {
        "harassment": "string",
        "hate_speech": "string",
        "sexually_explicit": "string",
        "dangerous_content": "string"
    }
}
```

#### POST /embed
Erstellt Embeddings für Text.

**Request Body:**
```json
{
    "text": "string",
    "model": "text-embedding-ada-002"
}
```

#### POST /embed-and-store
Erstellt ein Embedding und speichert es in der Vector DB.

**Request Body:**
```json
{
    "text": "string",
    "metadata": {
        "source": "string",
        "category": "string",
        "tags": ["string"],
        "custom_field": "value"
    }
}
```

#### POST /search-similar
Sucht ähnliche Texte basierend auf Embeddings.

**Request Body:**
```json
{
    "text": "string",
    "limit": 5,
    "score_threshold": 0.7,
    "filter": {
        "field": "value"
    }
}
```

**Response:**
```json
{
    "results": [
        {
            "id": "string",
            "text": "string",
            "score": 0.95,
            "metadata": {
                "source": "string",
                "category": "string",
                "tags": ["string"]
            }
        }
    ],
    "query_text": "string",
    "total_results": 5
}
```

#### POST /analyze-media
Analysiert ein Medium mit dem LLM Service.

**Request Body:**
```json
{
    "media_id": "string",
    "analysis_type": "full",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7
}
```

**Response:**
```json
{
    "media_id": "string",
    "analysis_type": "string",
    "media_analysis": {
        "content": "string",
        "metadata": {}
    },
    "llm_analysis": "string",
    "model": "string"
}
```

#### POST /describe-media
Generiert eine Beschreibung für ein Medium.

**Request Body:**
```json
{
    "media_id": "string",
    "style": "neutral",
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7
}
```

**Response:**
```json
{
    "description": "string"
}
```

#### POST /search-similar-media
Sucht ähnliche Medien.

**Request Body:**
```json
{
    "media_id": "string",
    "limit": 5,
    "model": "gpt-4"
}
```

**Response:**
```json
{
    "results": [
        {
            "media_id": "string",
            "similarity_score": 0.95,
            "metadata": {},
            "similarity_analysis": "string"
        }
    ]
}
```

#### GET /health
Health Check Endpoint.

**Response:**
```json
{
    "status": "healthy",
    "openai_models": 0,
    "anthropic_models": 0,
    "gemini_models": 0,
    "api_keys_valid": {
        "openai": true,
        "anthropic": true,
        "gemini": true
    }
}
```

#### GET /vector-health
Health Check für Vector DB Integration.

**Response:**
```json
{
    "status": "healthy",
    "collections": ["llm_embeddings"],
    "vector_size": 1536
}
```

#### GET /media-health
Health Check für Media Service Integration.

**Response:**
```json
{
    "status": "healthy",
    "media_count": 0,
    "analysis_types": ["full", "basic"]
}
```

#### POST /batch-embed
Speichert mehrere Embeddings in der Vector DB.

**Request Body:**
```json
{
    "texts": ["string"],
    "metadata_list": [
        {
            "source": "string",
            "category": "string",
            "tags": ["string"]
        }
    ]
}
```

**Response:**
```json
{
    "success": true
}
```

#### POST /search-metadata
Sucht Embeddings nach Metadaten.

**Request Body:**
```json
{
    "metadata_filter": {
        "category": "string",
        "tags": ["string"]
    },
    "limit": 5
}
```

**Response:**
```json
{
    "results": [
        {
            "id": "string",
            "text": "string",
            "metadata": {
                "source": "string",
                "category": "string",
                "tags": ["string"]
            }
        }
    ]
}
```

#### PATCH /update-metadata
Aktualisiert die Metadaten eines Embeddings.

**Request Body:**
```json
{
    "vector_id": "string",
    "new_metadata": {
        "category": "string",
        "tags": ["string"]
    }
}
```

**Response:**
```json
{
    "success": true
}
```

#### GET /collection-stats
Gibt Statistiken über die Collection zurück.

**Response:**
```json
{
    "vector_count": 0,
    "index_type": "string",
    "dimensions": 1536,
    "distance_metric": "Cosine"
}
```

#### POST /create-index
Erstellt einen Index für die Collection.

**Request Body:**
```json
{
    "index_type": "HNSW"
}
```

**Response:**
```json
{
    "success": true
}
```

#### DELETE /collection
Löscht die Collection.

**Response:**
```json
{
    "success": true
}
```

## Installation

1. Docker Image bauen:
```bash
docker build -t llm-service .
```

2. Service starten:
```bash
docker run -d -p 8003:8000 \
    -e OPENAI_API_KEY=your-key \
    -e ANTHROPIC_API_KEY=your-key \
    -e GOOGLE_API_KEY=your-key \
    -e VECTOR_DB_URL=http://vector-db:8000 \
    -e MEDIA_SERVICE_URL=http://media-service:8000 \
    -e ANALYTICS_SERVICE_URL=http://analytics-service:8000 \
    -e CACHE_SERVICE_URL=http://cache-service:8000 \
    -e MONITORING_SERVICE_URL=http://monitoring-service:8000 \
    llm-service
```

## Konfiguration

### Umgebungsvariablen
- `OPENAI_API_KEY`: OpenAI API-Key
- `ANTHROPIC_API_KEY`: Anthropic API-Key
- `GOOGLE_API_KEY`: Google API-Key
- `VECTOR_DB_URL`: URL des Vector DB Services
- `MEDIA_SERVICE_URL`: URL des Media Services
- `ANALYTICS_SERVICE_URL`: URL des Analytics Services
- `CACHE_SERVICE_URL`: URL des Cache Services
- `MONITORING_SERVICE_URL`: URL des Monitoring Services
- `PYTHONUNBUFFERED`: Python Output-Buffering deaktivieren

## Beispiele

### GPT-4 Beispiel
```python
{
    "prompt": "Erkläre mir die Quantenmechanik in einfachen Worten.",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system_prompt": "Du bist ein hilfreicher Assistent."
}
```

### Claude Beispiel
```python
{
    "prompt": "Analysiere den Text auf Sentiment.",
    "model": "claude-3-opus-20240229",
    "max_tokens": 500,
    "temperature": 0.5
}
```

### Gemini Beispiel mit Safety Settings
```python
{
    "prompt": "Beschreibe die Vorteile von KI.",
    "model": "gemini-pro",
    "safety_settings": {
        "harassment": "block_medium_and_above",
        "hate_speech": "block_high_and_above"
    }
}
```

### Gemini Beispiel ohne Safety Settings
```python
{
    "prompt": "Diskutiere kontroverse Themen.",
    "model": "gemini-pro",
    "safety_settings": {
        "disabled": true
    }
}
```

### Embedding erstellen und speichern
```python
{
    "text": "Dies ist ein Beispieltext für die semantische Suche.",
    "metadata": {
        "source": "dokumentation",
        "category": "beispiel",
        "tags": ["semantisch", "suche", "embedding"]
    }
}
```

### Ähnliche Texte suchen
```python
{
    "text": "Wie funktioniert die semantische Suche?",
    "limit": 3,
    "score_threshold": 0.8,
    "filter": {
        "category": "beispiel"
    }
}
```

### Medium analysieren
```python
{
    "media_id": "video_123",
    "analysis_type": "full",
    "model": "gpt-4",
    "max_tokens": 1000,
    "temperature": 0.7
}
```

### Medium beschreiben
```python
{
    "media_id": "image_456",
    "style": "technical",
    "model": "gpt-4",
    "max_tokens": 500,
    "temperature": 0.7
}
```

### Ähnliche Medien suchen
```python
{
    "media_id": "audio_789",
    "limit": 5,
    "model": "gpt-4"
}
```

## Vector DB Integration

### Collection
- Name: `llm_embeddings`
- Vector-Größe: 1536 (OpenAI Embeddings)
- Distanz-Metrik: Cosine Similarity

### Features
- Automatische Collection-Erstellung
- Embedding-Speicherung mit Metadaten
- Batch-Speicherung von Embeddings
- Semantische Suche
- Metadaten-basierte Suche
- Metadaten-Aktualisierung
- Collection-Statistiken
- Index-Erstellung (HNSW)
- Collection-Management
- Score-Threshold für Relevanz
- Filtering nach Metadaten
- Health Monitoring

### Index-Typen
- HNSW (Hierarchical Navigable Small World)
  - Schnelle Annäherungssuche
  - Gute Balance zwischen Geschwindigkeit und Genauigkeit
  - Empfohlen für die meisten Anwendungsfälle

### Metadaten
- Automatische Zeitstempel
- Benutzerdefinierte Felder
- Kategorisierung
- Tags
- Quelle
- Benutzer-ID
- Version

### Batch-Operationen
- Effiziente Speicherung mehrerer Embeddings
- Atomare Transaktionen
- Fehlerbehandlung pro Embedding
- Fortschritts-Tracking

### Suche
- Semantische Suche
- Metadaten-Filterung
- Score-Threshold
- Limitierung der Ergebnisse
- Sortierung nach Relevanz

### Verwaltung
- Collection-Statistiken
- Index-Management
- Collection-Löschung
- Health Monitoring
- Fehlerbehandlung

## Media Service Integration

### Features
- Medienanalyse mit LLM
- Automatische Beschreibungsgenerierung
- Ähnlichkeitssuche für Medien
- Verschiedene Analysetypen
- Anpassbare Beschreibungsstile
- Health Monitoring

## Fehlerbehandlung

Der Service implementiert umfangreiche Fehlerbehandlung:
- Validierung der Eingabedaten
- Exception Handling für alle Operationen
- Logging von Fehlern und Warnungen
- API-Key Validierung
- Service-Verbindungsprüfung

## Performance

- Effiziente Textgenerierung
- Kontextunterstützung
- Optimierte Token-Nutzung
- Caching (konfigurierbar)
- Schnelle Vektorsuche
- Parallele Medienanalyse

## Sicherheit

- API-Key Validierung
- Input-Validierung
- Exception Handling
- Rate Limiting (konfigurierbar)
- Safety Settings für Gemini
- Service-Zugriffskontrolle

## Monitoring

- Health Check Endpoints
- Logging
- API-Status
- Token-Nutzung
- Service-Status

## Bekannte Einschränkungen

- Maximale Token-Länge pro Request
- Modell-spezifische Einschränkungen
- Rate Limits der APIs
- Kosten pro Token
- Service-Speicherlimit

## Roadmap

- [ ] Batch-Processing optimieren
- [ ] Streaming-Unterstützung
- [ ] Zusätzliche Modelle
- [ ] Erweiterte Safety Settings
- [ ] Caching-System
- [ ] Kosten-Tracking
- [ ] Service Sharding
- [ ] Backup-System

## Service Integration

### Analytics Service
- Tracking von Embedding-Nutzung
- Statistiken pro Embedding
- Nutzungsanalysen
- Performance-Metriken

### Cache Service
- Embedding-Caching
- TTL-Konfiguration
- Cache-Invalidierung
- Performance-Optimierung

### Monitoring Service
- Request-Tracking
- Fehler-Tracking
- Service-Metriken
- Performance-Monitoring

### Konfiguration
```bash
docker run -d -p 8003:8000 \
    -e OPENAI_API_KEY=your-key \
    -e ANTHROPIC_API_KEY=your-key \
    -e GOOGLE_API_KEY=your-key \
    -e VECTOR_DB_URL=http://vector-db:8000 \
    -e MEDIA_SERVICE_URL=http://media-service:8000 \
    -e ANALYTICS_SERVICE_URL=http://analytics-service:8000 \
    -e CACHE_SERVICE_URL=http://cache-service:8000 \
    -e MONITORING_SERVICE_URL=http://monitoring-service:8000 \
    llm-service
```

### Neue Endpoints

#### GET /services-health
Health Check für alle Services.

**Response:**
```json
{
    "vector_db": {
        "status": "healthy",
        "collections": ["llm_embeddings"]
    },
    "media": {
        "status": "healthy",
        "media_count": 0
    },
    "analytics": {
        "status": "healthy",
        "tracking_enabled": true
    },
    "cache": {
        "status": "healthy",
        "cache_size": 0
    },
    "monitoring": {
        "status": "healthy",
        "metrics_enabled": true
    }
}
```

#### GET /analytics/embedding/{embedding_id}
Gibt Statistiken für ein Embedding zurück.

**Response:**
```json
{
    "embedding_id": "string",
    "usage_count": 0,
    "last_used": "2024-02-29T12:00:00Z",
    "usage_types": {
        "search": 0,
        "store": 0
    },
    "performance": {
        "avg_response_time": 0.0,
        "success_rate": 1.0
    }
}
```

#### GET /monitoring/metrics/{service}
Gibt Metriken für einen Service zurück.

**Response:**
```json
{
    "service": "string",
    "requests": {
        "total": 0,
        "success": 0,
        "error": 0
    },
    "performance": {
        "avg_response_time": 0.0,
        "p95_response_time": 0.0,
        "p99_response_time": 0.0
    },
    "errors": {
        "total": 0,
        "by_type": {}
    }
}
```

### Analytics Service Integration

#### Features
- Embedding-Nutzung verfolgen
- Statistiken pro Embedding
- Nutzungsanalysen
- Performance-Metriken
- Benutzerdefinierte Metriken

#### Tracking
- Automatisches Tracking
- Benutzerdefinierte Events
- Kontext-Informationen
- Zeitstempel

#### Statistiken
- Nutzungshäufigkeit
- Erfolgsrate
- Antwortzeiten
- Fehlerraten

### Cache Service Integration

#### Features
- Embedding-Caching
- TTL-Konfiguration
- Cache-Invalidierung
- Performance-Optimierung

#### Caching
- Automatisches Caching
- TTL-basiert
- LRU-Strategie
- Cache-Invalidierung

#### Performance
- Schnelle Abfragen
- Reduzierte API-Aufrufe
- Speicheroptimierung
- Cache-Statistiken

### Monitoring Service Integration

#### Features
- Request-Tracking
- Fehler-Tracking
- Service-Metriken
- Performance-Monitoring

#### Tracking
- API-Anfragen
- Fehler
- Performance
- Ressourcennutzung

#### Metriken
- Request-Volumen
- Erfolgsrate
- Antwortzeiten
- Fehlerraten

### Best Practices

#### Analytics
- Relevante Metriken tracken
- Kontext-Informationen sammeln
- Performance überwachen
- Trends analysieren

#### Caching
- Sinnvolle TTLs setzen
- Cache-Invalidierung planen
- Speicher überwachen
- Performance optimieren

#### Monitoring
- Wichtige Metriken tracken
- Alerts konfigurieren
- Performance überwachen
- Probleme früh erkennen 
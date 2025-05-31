# API-Dokumentation

## Vision Pipeline API

### Basis-URL
```
http://localhost:8000
```

### Endpunkte

#### POST /analyze/videos
Analysiert ein oder mehrere Videos.

**Request Body:**
```json
{
  "videos": [
    {
      "url": "string",
      "title": "string",
      "description": "string",
      "tags": ["string"]
    }
  ],
  "options": {
    "frame_sampling_rate": 1,
    "batch_size": 4,
    "priority": 1
  }
}
```

**Response:**
```json
{
  "job_id": "string",
  "status": "queued",
  "message": "string"
}
```

#### GET /jobs/{job_id}
Gibt den Status eines Jobs zurück.

**Response:**
```json
{
  "job_id": "string",
  "status": "string",
  "progress": 0,
  "results": {}
}
```

## Face Re-Identification API

### Basis-URL
```
http://localhost:8001
```

### Endpunkte

#### POST /analyze
Analysiert ein Bild auf Gesichter.

**Request Body:**
```json
{
  "image_data": "base64_string",
  "job_id": "string",
  "media_id": "string",
  "source_type": "string",
  "detect_faces": true,
  "extract_embeddings": true,
  "min_face_size": 20,
  "confidence_threshold": 0.5
}
```

**Response:**
```json
{
  "faces": [
    {
      "bbox": [x, y, w, h],
      "confidence": 0.95,
      "embedding": [float],
      "landmarks": [[x, y]],
      "attributes": {
        "age": 25,
        "gender": "male"
      }
    }
  ]
}
```

## Vector DB API

### Basis-URL
```
http://localhost:8002
```

### Endpunkte

#### POST /collections
Erstellt eine neue Collection.

**Request Body:**
```json
{
  "name": "string",
  "vector_size": 512,
  "distance": "Cosine"
}
```

#### POST /vectors
Speichert Vektoren in einer Collection.

**Request Body:**
```json
{
  "collection": "string",
  "vectors": [
    {
      "id": "string",
      "vector": [float],
      "metadata": {}
    }
  ]
}
```

#### POST /search
Sucht nach ähnlichen Vektoren.

**Request Body:**
```json
{
  "collection": "string",
  "vector": [float],
  "limit": 10,
  "score_threshold": 0.7
}
```

## LLM Service API

### Basis-URL
```
http://localhost:8003
```

### Endpunkte

#### POST /generate
Generiert Text mit dem gewählten LLM.

**Request Body:**
```json
{
  "prompt": "string",
  "max_tokens": 100,
  "temperature": 0.7,
  "model": "string"
}
```

## Whisper Service API

### Basis-URL
```
http://localhost:8004
```

### Endpunkte

#### POST /transcribe
Transkribiert Audio in Text.

**Request Body:**
```json
{
  "audio_data": "base64_string",
  "language": "de",
  "model": "base"
}
```

## NSFW Detection API

### Basis-URL
```
http://localhost:8005
```

### Endpunkte

#### POST /analyze
Analysiert ein Bild auf NSFW-Inhalte.

**Request Body:**
```json
{
  "image_data": "base64_string",
  "threshold": 0.5
}
```

**Response:**
```json
{
  "nsfw_score": 0.1,
  "categories": {
    "nude": 0.1,
    "explicit": 0.05,
    "violence": 0.02
  }
}
```

## Pose Estimation API

### Basis-URL
```
http://localhost:8006
```

### Endpunkte

#### POST /analyze
Analysiert die Pose in einem Bild.

**Request Body:**
```json
{
  "image_data": "base64_string"
}
```

**Response:**
```json
{
  "keypoints": [[x, y, confidence]],
  "scores": [float],
  "num_people": 1
}
```

## OCR Detection API

### Basis-URL
```
http://localhost:8007
```

### Endpunkte

#### POST /analyze
Erkennt Text in einem Bild.

**Request Body:**
```json
{
  "image_data": "base64_string"
}
```

**Response:**
```json
{
  "text": "string",
  "confidence": 0.95,
  "bbox": [[x, y, w, h]],
  "language": "de"
}
```

## Guardrails API

### Basis-URL
```
http://localhost:8008
```

### Endpunkte

#### POST /validate/request
Validiert eine Anfrage.

**Request Body:**
```json
{
  "request_data": {},
  "request_type": "string"
}
```

## Allgemeine Hinweise

### Authentifizierung
Alle API-Endpunkte erfordern eine Authentifizierung über JWT-Token im Authorization-Header:
```
Authorization: Bearer <token>
```

### Rate Limiting
- Standard: 60 Anfragen pro Minute
- Batch-Operationen: 10 Anfragen pro Minute

### Fehlercodes
- 400: Ungültige Anfrage
- 401: Nicht authentifiziert
- 403: Keine Berechtigung
- 404: Ressource nicht gefunden
- 429: Zu viele Anfragen
- 500: Interner Serverfehler

### Batch-Verarbeitung
Für effiziente Verarbeitung großer Datenmengen:
- Maximale Batch-Größe: 32 Bilder/Videos
- Empfohlene Batch-Größe: 4-8 für optimale GPU-Auslastung

### Caching
- Redis-basiertes Caching für häufig abgerufene Ergebnisse
- Cache-TTL: 1 Stunde
- Cache-Invalidierung bei Updates 

## Performance-Optimierungen

### GPU-Optimierungen
- **CUDA-Optimierungen**:
  - Automatische Batch-Größenanpassung basierend auf GPU-Speicher
  - CUDA Graph-Optimierung für wiederholte Operationen
  - Mixed Precision Training (FP16) wo möglich
  - TensorRT-Optimierung für Inferenz

- **GPU-Ressourcen-Management**:
  - Dynamische GPU-Zuweisung basierend auf Workload
  - Automatische Lastverteilung auf mehrere GPUs
  - GPU-Speicher-Management mit automatischer Bereinigung

### Batch-Verarbeitung
- **Optimale Batch-Größen**:
  - Bilder: 8-16 pro Batch
  - Videos: 4-8 pro Batch
  - Text: 32-64 pro Batch

- **Batch-Strategien**:
  - Dynamische Batch-Größenanpassung
  - Priorisierung von Batch-Jobs
  - Batch-Zusammenführung für ähnliche Anfragen

### Caching-Strategien
- **Mehrstufiges Caching**:
  - L1: In-Memory Cache (Redis)
  - L2: Disk Cache für große Daten
  - L3: Distributed Cache für Cluster

- **Cache-Optimierungen**:
  - Predictive Caching für häufig abgerufene Daten
  - Cache-Warming für erwartete Anfragen
  - Cache-Invalidierung mit Versionierung

### Netzwerk-Optimierungen
- **Komprimierung**:
  - GZIP für Text-Responses
  - JPEG/WebP für Bilder
  - H.264/H.265 für Videos

- **Streaming**:
  - Chunked Transfer für große Dateien
  - Progressive Loading für Videos
  - WebSocket für Echtzeit-Updates

### Datenbank-Optimierungen
- **Vector DB**:
  - HNSW-Index für schnelle Ähnlichkeitssuche
  - Quantisierung für reduzierte Speichernutzung
  - Sharding für horizontale Skalierung

- **Redis**:
  - Pipeline-Operationen für Batch-Anfragen
  - Pub/Sub für Echtzeit-Updates
  - Persistenz mit RDB und AOF

### API-Optimierungen
- **Request-Optimierungen**:
  - GraphQL für flexible Datenabfragen
  - Field Selection für reduzierte Payload
  - Pagination für große Datensätze

- **Response-Optimierungen**:
  - Lazy Loading für große Objekte
  - Delta-Updates für inkrementelle Änderungen
  - Response-Compression

### Monitoring und Skalierung
- **Performance-Metriken**:
  - Response-Zeiten
  - GPU-Auslastung
  - Cache-Hit-Rate
  - Batch-Verarbeitungszeiten

- **Skalierungsstrategien**:
  - Horizontale Skalierung mit Load Balancing
  - Vertikale Skalierung mit GPU-Upgrades
  - Auto-Scaling basierend auf Last

### Best Practices
1. **Anfrage-Optimierung**:
   - Verwenden Sie Batch-Anfragen wo möglich
   - Nutzen Sie Caching für wiederholte Anfragen
   - Implementieren Sie Retry-Logik mit exponentieller Backoff

2. **Daten-Optimierung**:
   - Komprimieren Sie große Dateien vor dem Upload
   - Verwenden Sie effiziente Bildformate (WebP)
   - Implementieren Sie Progressive Loading

3. **Client-Optimierung**:
   - Implementieren Sie Client-seitiges Caching
   - Nutzen Sie WebSocket für Echtzeit-Updates
   - Implementieren Sie Request-Deduplizierung 
# API-Dokumentation

## Überblick

Diese API ermöglicht die automatisierte Analyse und Verarbeitung von Medieninhalten. Sie ist als eine Sammlung von Microservices konzipiert, die über ein API-Gateway (z.B. Nginx) angesprochen werden können.

Jeder Kernservice, der über eine HTTP-Schnittstelle verfügt und mit FastAPI erstellt wurde, bietet eine automatisch generierte, interaktive API-Dokumentation über Swagger UI und ReDoc.

## Interaktive API-Dokumentation (Swagger UI / ReDoc)

Die detaillierteste und aktuellste Dokumentation für die Endpunkte der einzelnen Services finden Sie direkt in der von FastAPI generierten Swagger UI bzw. ReDoc.

Standardmäßig sind diese für jeden Service unter folgenden Pfaden relativ zur Basis-URL des jeweiligen Services erreichbar:

-   **Swagger UI**: `/docs`
-   **ReDoc**: `/redoc`

**Beispielhafter Zugriff über ein API-Gateway (Nginx):**

Wenn die Services über ein API-Gateway (wie Nginx) unter spezifischen Pfaden zugänglich gemacht werden, würden Sie die Dokumentation wie folgt erreichen (Beispiele):

-   Vision Pipeline Service: `http://<Ihr-Gateway-Host>/api/vision_pipeline/docs`
-   Face Re-ID Service: `http://<Ihr-Gateway-Host>/api/face_reid/docs`
-   Job Manager Service: `http://<Ihr-Gateway-Host>/api/job_manager/docs`

Die genauen Pfade hängen von Ihrer Nginx-Konfiguration ab.

## Allgemeine Konzepte

### Authentifizierung

Die Authentifizierung erfolgt in der Regel über API-Keys, die im `Authorization`-Header als Bearer-Token gesendet werden.

```http
Authorization: Bearer <your_api_key>
```

Details zu spezifischen Authentifizierungsanforderungen entnehmen Sie bitte der jeweiligen Service-Dokumentation (Swagger UI) oder den Konfigurationsdetails des Services.

### Fehlerbehandlung

Die API verwendet Standard-HTTP-Statuscodes zur Signalisierung von Erfolg oder Misserfolg von Anfragen.

Typische Fehlercodes:

| Code | Beschreibung                     |
| :--- | :------------------------------- |
| 200  | OK                               |
| 201  | Created                          |
| 202  | Accepted (z.B. für asynchrone Jobs) |
| 400  | Bad Request (Ungültige Anfrage)   |
| 401  | Unauthorized (Fehlende/Ungültige Auth) |
| 403  | Forbidden (Keine Berechtigung)    |
| 404  | Not Found (Ressource nicht gefunden)|
| 429  | Too Many Requests (Rate Limiting) |
| 500  | Internal Server Error            |
| 503  | Service Unavailable              |

Spezifische Fehlerdetails werden oft im Response Body als JSON zurückgegeben.

### Rate Limiting

Einige Endpunkte können Rate Limiting unterliegen, um eine faire Nutzung zu gewährleisten und Überlastung zu vermeiden. Die genauen Limits entnehmen Sie bitte den jeweiligen Service-Dokumentationen oder den API-Antworten (z.B. `X-RateLimit-Limit`, `X-RateLimit-Remaining` Header oder Fehlercode 429).

### Asynchrone Operationen und Jobs

Länger laufende Operationen, wie die Analyse großer Videodateien, werden oft als asynchrone Jobs implementiert. In solchen Fällen gibt ein API-Aufruf typischerweise eine Job-ID zurück. Der Status dieses Jobs kann dann über einen separaten Endpunkt abgefragt werden.

Beispiel (konzeptionell):

1.  `POST /analyze/videos` -> `HTTP 202 Accepted` mit `{"job_id": "some-uuid"}`
2.  `GET /jobs/{job_id}` -> `HTTP 200 OK` mit `{"status": "processing", "progress": 50}`

Die genauen Endpunkte und Modelle hierfür finden Sie in der Swagger UI der entsprechenden Services (z.B. Vision Pipeline, Job Manager).

## Haupt-Servicebereiche (Beispiele)

Eine detaillierte Beschreibung der Endpunkte für jeden Service finden Sie in deren jeweiliger Swagger UI (`/docs`).

-   **Vision Pipeline API**: Zuständig für die Orchestrierung der Bild- und Videoanalyse.
-   **Face Re-Identification API**: Stellt Funktionen zur Gesichtserkennung und zum Abgleich bereit.
-   **Vector DB API**: Schnittstelle zur Vektordatenbank für Ähnlichkeitssuchen.
-   **LLM Service API**: Ermöglicht Interaktionen mit Sprachmodellen.
-   **Whisper Service API**: Für Audio-Transkription.
-   **NSFW Detection API**: Zur Erkennung von potenziell sensiblen Inhalten.
-   **Pose Estimation API**: Für die Analyse von Körperhaltungen.
-   **OCR Detection API**: Zur Texterkennung in Bildern.
-   **Job Manager API**: Verwaltung und Überwachung von Hintergrund-Jobs.

Bitte konsultieren Sie die `/docs` Endpunkte der jeweiligen Services für eine vollständige und interaktive API-Referenz.

## Endpunkte

### Frame-Analyse

#### Einzelne Frame-Analyse
```http
POST /analyze/frame
Content-Type: application/json

{
    "frame": [...],  // Base64-kodiertes Bild
    "audio_data": [...],  // Optional: Audio-Daten
    "sample_rate": 44100  // Optional: Audio-Sampling-Rate
}
```

#### Response
```json
{
    "status": "success",
    "data": {
        "restraints": [
            {
                "type": "string",
                "confidence": 0.95,
                "location": [x, y, width, height]
            }
        ],
        "safety_score": 0.8,
        "consent_indicators": [...],
        "monitoring_status": "active",
        "audio_analysis": {
            "distress_detected": false,
            "safeword_detected": false
        },
        "processing_info": {
            "processing_time": 0.5,
            "gpu_cost": {
                "usd": 0.001,
                "eur": 0.0009
            }
        }
    }
}
```

### Batch-Analyse

#### Mehrere Frames analysieren
```http
POST /analyze/batch
Content-Type: application/json

{
    "frames": [[...], [...]],  // Array von Base64-kodierten Bildern
    "audio_data": [[...], [...]],  // Optional: Array von Audio-Daten
    "sample_rates": [44100, 44100]  // Optional: Array von Sampling-Rates
}
```

#### Response
```json
{
    "status": "success",
    "data": {
        "results": [
            {
                "frame_id": 0,
                "restraints": [...],
                "safety_score": 0.8,
                "consent_indicators": [...],
                "monitoring_status": "active",
                "audio_analysis": {...}
            }
        ],
        "batch_info": {
            "total_frames": 2,
            "processing_time": 1.2,
            "gpu_cost": {
                "usd": 0.002,
                "eur": 0.0018
            }
        }
    }
}
```

### Instanz-Management

#### Instanz-Status abrufen
```http
GET /instances/status
```

#### Response
```json
{
    "status": "success",
    "data": {
        "instances": [
            {
                "id": "instance-1",
                "provider": "vast_ai",
                "type": "rtx_3090",
                "status": "running",
                "load": 0.75,
                "cost": {
                    "usd": 0.45,
                    "eur": 0.41
                }
            }
        ],
        "total_cost": {
            "usd": 0.45,
            "eur": 0.41
        }
    }
}
```

## Fehlercodes

| Code | Beschreibung |
|------|--------------|
| 400  | Ungültige Anfrage |
| 401  | Nicht autorisiert |
| 403  | Zugriff verweigert |
| 404  | Ressource nicht gefunden |
| 429  | Zu viele Anfragen |
| 500  | Server-Fehler |

### Fehler-Response
```json
{
    "status": "error",
    "error": {
        "code": 400,
        "message": "Ungültige Anfrage",
        "details": {...}
    }
}
```

## Rate Limiting

- 100 Anfragen pro Minute
- 1000 Anfragen pro Stunde
- 10000 Anfragen pro Tag

## Versionierung

Die API-Version wird im URL-Pfad angegeben:
```http
https://api.example.com/v1/analyze/frame
```

## WebSocket-Endpunkte

### Echtzeit-Analyse
```http
WS /ws/analyze
```

#### Nachrichten-Format
```json
{
    "type": "frame",
    "data": {
        "frame": [...],
        "audio_data": [...]
    }
}
```

## Beispiele

### Python
```python
import aiohttp
import base64

async def analyze_frame(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.example.com/v1/analyze/frame',
            json={
                'frame': image_data
            },
            headers={
                'Authorization': f'Bearer {API_KEY}'
            }
        ) as response:
            return await response.json()
```

### JavaScript
```javascript
async function analyzeFrame(imageFile) {
    const base64 = await convertToBase64(imageFile);
    
    const response = await fetch('https://api.example.com/v1/analyze/frame', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            frame: base64
        })
    });
    
    return await response.json();
}
```

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
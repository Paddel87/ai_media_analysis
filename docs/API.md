# API-Dokumentation

## Übersicht

Die API des AI Media Analysis Systems bietet Endpunkte für die Verarbeitung und Analyse von Medieninhalten.

## Basis-URL

```
http://localhost:8000
```

## Authentifizierung

Alle API-Endpunkte erfordern Authentifizierung über API-Key im Header:

```
Authorization: Bearer <api_key>
```

## Endpunkte

### Job Management

#### Jobs erstellen
```http
POST /jobs
```

**Request Body:**
```json
{
    "file_path": "string",
    "file_type": "string",
    "priority": "normal|high|low",
    "job_name": "string",
    "context": "string",
    "source_type": "local|cloud"
}
```

**Response:**
```json
{
    "job_id": "string",
    "status": "pending|processing|completed|failed",
    "created_at": "datetime"
}
```

#### Job Status abrufen
```http
GET /jobs/{job_id}
```

**Response:**
```json
{
    "job_id": "string",
    "status": "string",
    "progress": "float",
    "results": "object",
    "error": "string"
}
```

### Vision Pipeline

#### Bildanalyse
```http
POST /analyze/image
```

**Request Body:**
```json
{
    "image_data": "base64_string",
    "analysis_types": ["nsfw", "restraint", "ocr", "face"]
}
```

**Response:**
```json
{
    "nsfw_score": "float",
    "restraints": ["array"],
    "ocr_text": "string",
    "faces": ["array"]
}
```

#### Videoanalyse
```http
POST /analyze/video
```

**Request Body:**
```json
{
    "video_path": "string",
    "frame_sampling": "integer",
    "analysis_types": ["array"]
}
```

**Response:**
```json
{
    "job_id": "string",
    "estimated_duration": "integer"
}
```

### Audio-Analyse

#### Transkription
```http
POST /transcribe
```

**Request Body:**
```json
{
    "audio_data": "base64_string",
    "language": "string"
}
```

**Response:**
```json
{
    "text": "string",
    "segments": ["array"],
    "language": "string"
}
```

### Personendossier

#### Dossier erstellen
```http
POST /dossiers
```

**Request Body:**
```json
{
    "temporary_id": "string",
    "display_name": "string",
    "notes": "string"
}
```

**Response:**
```json
{
    "dossier_id": "string",
    "created_at": "datetime"
}
```

#### Dossier aktualisieren
```http
PUT /dossiers/{dossier_id}
```

**Request Body:**
```json
{
    "display_name": "string",
    "notes": "string",
    "metadata": "object"
}
```

#### Dossier abrufen
```http
GET /dossiers/{dossier_id}
```

**Response:**
```json
{
    "dossier_id": "string",
    "temporary_id": "string",
    "display_name": "string",
    "notes": "string",
    "face_instances": ["array"],
    "media_appearances": ["array"],
    "emotion_stats": "object",
    "restraint_stats": "object"
}
```

## Fehlerbehandlung

### Fehlercodes

- `400` - Ungültige Anfrage
- `401` - Nicht authentifiziert
- `403` - Keine Berechtigung
- `404` - Ressource nicht gefunden
- `500` - Server-Fehler

### Fehler-Response
```json
{
    "error": "string",
    "message": "string",
    "details": "object"
}
```

## Rate Limiting

- 100 Anfragen pro Minute pro API-Key
- 1000 Anfragen pro Stunde pro API-Key

## Versionierung

Die API-Version wird im URL-Pfad angegeben:

```
http://localhost:8000/v1/jobs
```

## Beispiele

### Python
```python
import requests

api_key = "your_api_key"
headers = {"Authorization": f"Bearer {api_key}"}

# Job erstellen
response = requests.post(
    "http://localhost:8000/v1/jobs",
    headers=headers,
    json={
        "file_path": "/path/to/file.mp4",
        "file_type": "video",
        "priority": "normal",
        "job_name": "Test Job"
    }
)
```

### JavaScript
```javascript
const apiKey = "your_api_key";
const headers = {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json"
};

// Job erstellen
fetch("http://localhost:8000/v1/jobs", {
    method: "POST",
    headers: headers,
    body: JSON.stringify({
        file_path: "/path/to/file.mp4",
        file_type: "video",
        priority: "normal",
        job_name: "Test Job"
    })
});
``` 
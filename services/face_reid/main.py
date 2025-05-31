from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import cv2
import logging
from typing import List, Dict, Optional, Tuple, Any
import insightface
from insightface.app import FaceAnalysis
import os
import json
from datetime import datetime
import uuid
import requests
import io
import base64
import redis
import pickle
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_reid_service")

app = FastAPI(
    title="Face Re-Identification Service",
    description="Service für Gesichtserkennung und Re-Identification in Bildern und Videos"
)

# Redis-Konfiguration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Thread Pool für CPU-intensive Operationen
thread_pool = ThreadPoolExecutor(max_workers=4)

class ImageAnalysisRequest(BaseModel):
    image_data: bytes
    job_id: str
    media_id: str
    source_type: str
    detect_faces: bool = True
    extract_embeddings: bool = True
    min_face_size: int = 20
    confidence_threshold: float = 0.5

class FaceDetectionResult(BaseModel):
    face_id: str
    bbox: Dict[str, int]  # x, y, w, h
    confidence: float
    landmarks: Optional[List[Dict[str, float]]] = None
    embedding: Optional[List[float]] = None
    job_id: str
    media_id: str
    source_type: str
    timestamp: str

class AnalysisResult(BaseModel):
    faces: List[FaceDetectionResult]
    error: Optional[str] = None

class BatchAnalysisRequest(BaseModel):
    images: List[ImageAnalysisRequest]
    batch_size: int = 4

class FaceReIDService:
    def __init__(self):
        self.clip_service_url = "http://clip-service:8000"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.face_analyzer = FaceAnalysis(name="buffalo_l", root="./models")
        self.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
        
        # Redis-Verbindung
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # Emotion-Kategorien für CLIP
        self.emotion_categories = [
            "happy face", "sad face", "angry face", "fearful face",
            "surprised face", "disgusted face", "neutral face",
            "pain expression", "pleasure expression"
        ]
        
        # Cache für Embeddings
        self.embedding_cache = {}
        
    async def analyze_face(self, image_data: bytes, job_id: str, media_id: str, source_type: str) -> Dict:
        """
        Analysiert ein Gesicht mit InsightFace und CLIP
        """
        try:
            # Bild in numpy Array konvertieren
            image = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            
            # Gesichtserkennung mit InsightFace
            faces = self.face_analyzer.get(image)
            
            if not faces:
                return {"error": "Kein Gesicht gefunden"}
            
            results = []
            for face in faces:
                # CLIP-Analyse für Emotionen
                response = requests.post(
                    f"{self.clip_service_url}/analyze",
                    json={
                        "image_data": base64.b64encode(image_data).decode(),
                        "text_queries": self.emotion_categories
                    }
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=500, detail="CLIP-Service nicht erreichbar")
                
                emotion_results = response.json()
                
                # Ergebnisse formatieren
                face_id = str(uuid.uuid4())
                result = {
                    "face_id": face_id,
                    "bbox": face.bbox.tolist(),
                    "landmarks": face.kps.tolist(),
                    "embedding": face.embedding.tolist(),
                    "confidence": float(face.det_score),
                    "emotions": emotion_results,
                    "job_id": job_id,
                    "media_id": media_id,
                    "source_type": source_type,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # In Redis speichern
                self._save_face_to_redis(face_id, result)
                
                results.append(result)
            
            return {"faces": results}
            
        except Exception as e:
            logger.error(f"Fehler bei der Gesichtsanalyse: {str(e)}")
            raise

    @lru_cache(maxsize=1000)
    async def compare_faces(self, face1_embedding: Tuple[float, ...], face2_embedding: Tuple[float, ...]) -> float:
        """
        Vergleicht zwei Gesichts-Embeddings mit Caching
        """
        try:
            face1 = np.array(face1_embedding)
            face2 = np.array(face2_embedding)
            
            # Kosinus-Ähnlichkeit berechnen
            similarity = np.dot(face1, face2) / (np.linalg.norm(face1) * np.linalg.norm(face2))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Fehler beim Vergleich der Gesichter: {str(e)}")
            raise

    async def find_matches(self, target_embedding: List[float], embeddings: List[List[float]], 
                          threshold: float = 0.5) -> List[Dict]:
        """
        Findet ähnliche Gesichter in einer Datenbank
        """
        try:
            matches = []
            target_embedding_tuple = tuple(target_embedding)
            
            # Parallelisierung für große Datenmengen
            tasks = []
            for i, embedding in enumerate(embeddings):
                embedding_tuple = tuple(embedding)
                tasks.append(self.compare_faces(target_embedding_tuple, embedding_tuple))
            
            similarities = await asyncio.gather(*tasks)
            
            for i, similarity in enumerate(similarities):
                if similarity >= threshold:
                    matches.append({
                        "index": i,
                        "similarity": similarity
                    })
            
            # Nach Ähnlichkeit sortieren
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            return matches
            
        except Exception as e:
            logger.error(f"Fehler bei der Suche nach Übereinstimmungen: {str(e)}")
            raise

    def _save_face_to_redis(self, face_id: str, face_data: Dict):
        """
        Speichert Gesichtsdaten in Redis
        """
        try:
            # Gesichtsdaten serialisieren
            face_data_bytes = pickle.dumps(face_data)
            
            # In Redis speichern
            self.redis_client.set(f"face:{face_id}", face_data_bytes)
            
            # Index für schnelle Suche
            self.redis_client.sadd("faces", face_id)
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern in Redis: {str(e)}")
            raise

    def get_face_history(self, face_id: str) -> Dict[str, Any]:
        """
        Gibt die Historie eines Gesichts zurück
        """
        try:
            face_data = self.redis_client.get(f"face:{face_id}")
            if not face_data:
                raise HTTPException(status_code=404, detail="Gesicht nicht gefunden")
            
            return pickle.loads(face_data)
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Gesichtshistorie: {str(e)}")
            raise

    async def process_batch(self, batch: List[ImageAnalysisRequest]) -> List[Dict]:
        """
        Verarbeitet einen Batch von Bildern
        """
        try:
            results = []
            for request in batch:
                result = await self.analyze_face(
                    request.image_data,
                    request.job_id,
                    request.media_id,
                    request.source_type
                )
                results.append(result)
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {str(e)}")
            raise

# Service-Instanz erstellen
face_reid_service = FaceReIDService()

@app.post("/analyze")
async def analyze_face(request: ImageAnalysisRequest):
    """
    Analysiert ein Gesicht
    """
    try:
        return await face_reid_service.analyze_face(
            request.image_data,
            request.job_id,
            request.media_id,
            request.source_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze_batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analysiert einen Batch von Bildern
    """
    try:
        # Batch in Chunks aufteilen
        chunks = [request.images[i:i + request.batch_size] 
                 for i in range(0, len(request.images), request.batch_size)]
        
        results = []
        for chunk in chunks:
            chunk_results = await face_reid_service.process_batch(chunk)
            results.extend(chunk_results)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_faces(request: FaceComparisonRequest):
    """
    Vergleicht zwei Gesichter
    """
    try:
        similarity = await face_reid_service.compare_faces(
            tuple(request.face1_embedding),
            tuple(request.face2_embedding)
        )
        return {"similarity": similarity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find_matches")
async def find_matches(request: FaceMatchRequest):
    """
    Findet ähnliche Gesichter
    """
    try:
        return await face_reid_service.find_matches(
            request.target_embedding,
            request.embeddings,
            request.threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/face/{face_id}")
async def get_face(face_id: str):
    """
    Gibt die Daten eines Gesichts zurück
    """
    try:
        return face_reid_service.get_face_history(face_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # Redis Health Check
        redis_healthy = face_reid_service.redis_client.ping()
        
        # CLIP-Service Health Check
        response = requests.get(f"{face_reid_service.clip_service_url}/health")
        clip_healthy = response.status_code == 200
        
        return {
            "status": "healthy" if redis_healthy and clip_healthy else "unhealthy",
            "redis": "available" if redis_healthy else "unavailable",
            "clip_service": "available" if clip_healthy else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
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

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_reid_service")

app = FastAPI(
    title="Face Re-Identification Service",
    description="Service für Gesichtserkennung und Re-Identification in Bildern und Videos"
)

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

class FaceReIDService:
    def __init__(self):
        self.clip_service_url = "http://clip-service:8000"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.face_analyzer = FaceAnalysis(name="buffalo_l", root="./models")
        self.face_analyzer.prepare(ctx_id=0, det_size=(640, 640))
        
        # Emotion-Kategorien für CLIP
        self.emotion_categories = [
            "happy face", "sad face", "angry face", "fearful face",
            "surprised face", "disgusted face", "neutral face",
            "pain expression", "pleasure expression"
        ]
        
    async def analyze_face(self, image_data: bytes) -> Dict:
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
            
            face = faces[0]  # Erstes erkanntes Gesicht
            
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
            result = {
                "face_id": str(uuid.uuid4()),
                "bbox": face.bbox.tolist(),
                "landmarks": face.kps.tolist(),
                "embedding": face.embedding.tolist(),
                "confidence": float(face.det_score),
                "emotions": emotion_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Gesichtsanalyse: {str(e)}")
            raise

    async def compare_faces(self, face1_embedding: List[float], face2_embedding: List[float]) -> float:
        """
        Vergleicht zwei Gesichts-Embeddings
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
            for i, embedding in enumerate(embeddings):
                similarity = await self.compare_faces(target_embedding, embedding)
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

    def get_face_history(self, face_id: str) -> Dict[str, Any]:
        """
        Gibt die Historie eines Gesichts zurück
        """
        if face_id not in self.face_database:
            raise HTTPException(status_code=404, detail="Gesicht nicht gefunden")
        return self.face_database[face_id]

# Service-Instanz erstellen
face_reid_service = FaceReIDService()

class FaceAnalysisRequest(BaseModel):
    image_data: bytes

class FaceComparisonRequest(BaseModel):
    face1_embedding: List[float]
    face2_embedding: List[float]

class FaceMatchRequest(BaseModel):
    target_embedding: List[float]
    embeddings: List[List[float]]
    threshold: float = 0.5

@app.post("/analyze")
async def analyze_face(request: FaceAnalysisRequest):
    """
    Analysiert ein Gesicht
    """
    try:
        return await face_reid_service.analyze_face(request.image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare")
async def compare_faces(request: FaceComparisonRequest):
    """
    Vergleicht zwei Gesichter
    """
    try:
        similarity = await face_reid_service.compare_faces(
            request.face1_embedding,
            request.face2_embedding
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

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # CLIP-Service Health Check
        response = requests.get(f"{face_reid_service.clip_service_url}/health")
        if response.status_code != 200:
            return {"status": "unhealthy", "clip_service": "unavailable"}
        return {"status": "healthy", "clip_service": "available"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
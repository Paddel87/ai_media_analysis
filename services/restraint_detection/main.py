import cv2
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import torch
from transformers import CLIPProcessor, CLIPModel
import asyncio
import aiohttp
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("restraint_detection")

app = FastAPI(
    title="Restraint Detection Service",
    description="Service zur Erkennung von Fesselungen und verwandten Materialien in Bildern und Videos",
    version="1.0.0"
)

class RestraintDetector:
    def __init__(self):
        """Initialisiert den Restraint Detector mit CLIP-Modell."""
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            # Kategorien für Fesselungen und Materialien
            self.categories = [
                "rope restraint", "handcuffs", "leather restraints", "tape restraint",
                "rope", "leather", "metal chains", "plastic wrap", "tape",
                "restraints", "cuffs", "gags", "blindfolds", "collars"
            ]
            
            # Text-Embeddings für die Kategorien vorberechnen
            self.category_embeddings = self._prepare_category_embeddings()
            
            logger.log_info("Restraint Detector initialisiert", extra={
                "device": self.device,
                "categories": self.categories
            })
        except Exception as e:
            logger.log_error("Fehler bei der Initialisierung des Restraint Detectors", error=e)
            raise

    def _prepare_category_embeddings(self) -> torch.Tensor:
        """Bereitet die Text-Embeddings für die Kategorien vor."""
        try:
            inputs = self.processor(
                text=self.categories,
                return_tensors="pt",
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            
            return text_features
        except Exception as e:
            logger.log_error("Fehler beim Vorbereiten der Kategorie-Embeddings", error=e)
            raise

    async def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analysiert ein einzelnes Frame auf Fesselungen und Materialien.
        
        Args:
            frame: Das zu analysierende Bild als numpy array
            
        Returns:
            Dictionary mit den Analyseergebnissen
        """
        try:
            # Bild vorbereiten
            image = self.processor(
                images=frame,
                return_tensors="pt"
            ).to(self.device)
            
            # Bild-Embedding berechnen
            with torch.no_grad():
                image_features = self.model.get_image_features(**image)
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Ähnlichkeiten berechnen
            similarity = (100.0 * image_features @ self.category_embeddings.T).softmax(dim=-1)
            
            # Ergebnisse formatieren
            results = []
            for idx, (category, score) in enumerate(zip(self.categories, similarity[0])):
                if score > 0.1:  # Nur relevante Ergebnisse
                    results.append({
                        "category": category,
                        "confidence": float(score)
                    })
            
            return {
                "restraint_data": {
                    "detections": results,
                    "has_restraints": len(results) > 0
                }
            }
        except Exception as e:
            logger.log_error("Fehler bei der Frame-Analyse", error=e)
            raise

    async def process_batch(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """
        Verarbeitet einen Batch von Frames.
        
        Args:
            frames: Liste von Frames als numpy arrays
            
        Returns:
            Liste von Analyseergebnissen
        """
        try:
            tasks = [self.analyze_frame(frame) for frame in frames]
            return await asyncio.gather(*tasks)
        except Exception as e:
            logger.log_error("Fehler bei der Batch-Verarbeitung", error=e)
            raise

# Detector-Instanz erstellen
detector = RestraintDetector()

class FrameRequest(BaseModel):
    """Request-Modell für die Frame-Analyse."""
    frame: List[int]  # Base64-kodiertes Bild

class BatchRequest(BaseModel):
    """Request-Modell für die Batch-Analyse."""
    frames: List[List[int]]  # Liste von Base64-kodierten Bildern

@app.post("/analyze/frame")
async def analyze_frame(request: FrameRequest) -> Dict[str, Any]:
    """
    Analysiert ein einzelnes Frame.
    
    Args:
        request: FrameRequest mit dem zu analysierenden Bild
        
    Returns:
        Analyseergebnisse
    """
    try:
        # Base64-Dekodierung
        frame = np.frombuffer(bytes(request.frame), dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Ungültiges Bildformat")
        
        result = await detector.analyze_frame(frame)
        return result
    except Exception as e:
        logger.log_error("Fehler bei der Frame-Analyse", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/batch")
async def analyze_batch(request: BatchRequest) -> List[Dict[str, Any]]:
    """
    Analysiert einen Batch von Frames.
    
    Args:
        request: BatchRequest mit den zu analysierenden Bildern
        
    Returns:
        Liste von Analyseergebnissen
    """
    try:
        # Base64-Dekodierung
        frames = []
        for frame_data in request.frames:
            frame = np.frombuffer(bytes(frame_data), dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            if frame is None:
                raise HTTPException(status_code=400, detail="Ungültiges Bildformat")
            frames.append(frame)
        
        results = await detector.process_batch(frames)
        return results
    except Exception as e:
        logger.log_error("Fehler bei der Batch-Analyse", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health Check Endpoint."""
    return {"status": "healthy"} 
import os
import logging
import torch
import clip
from PIL import Image
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import boto3
from dotenv import load_dotenv
import json
import cv2
import io
from transformers import CLIPProcessor, CLIPModel

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Umgebungsvariablen laden
load_dotenv()

# FastAPI App initialisieren
app = FastAPI(
    title="CLIP NSFW Detection Service",
    description="Service für NSFW-Erkennung in Bildern und Videos mit CLIP"
)

# CLIP Modell und Vorverarbeitung laden
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# NSFW-Kategorien
NSFW_CATEGORIES = [
    "nude", "explicit", "sexual", "violence", "gore",
    "safe", "appropriate", "family-friendly"
]

class ImageAnalysisRequest(BaseModel):
    image_data: bytes
    threshold: float = 0.5
    batch_size: int = 4

class NSFWResult(BaseModel):
    is_nsfw: bool
    confidence: float
    categories: Dict[str, float]
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    results: List[NSFWResult]
    processing_time: float
    device: str

class CLIPNSFWService:
    def __init__(self):
        self.model = None
        self.processor = None
        self.categories = [
            "nude", "explicit", "violence", "gore", "sexual content",
            "inappropriate", "adult content", "disturbing content"
        ]
        self.initialize_model()
        
    def initialize_model(self):
        try:
            # CLIP Modell initialisieren
            model_name = "openai/clip-vit-base-patch32"
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model = CLIPModel.from_pretrained(model_name)
            self.model.eval()
            
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                
            logger.info("CLIP NSFW Modell erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des CLIP Modells: {str(e)}")
            raise

    def analyze_image(self, image_data: bytes, threshold: float = 0.5) -> NSFWResult:
        try:
            # Bild in numpy array konvertieren
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Bild für CLIP vorbereiten
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Text-Prompts für NSFW-Kategorien
            text_inputs = [f"a photo of {category}" for category in self.categories]
            
            # Bild und Text verarbeiten
            inputs = self.processor(
                images=pil_image,
                text=text_inputs,
                return_tensors="pt",
                padding=True
            )
            
            # Auf GPU verschieben wenn verfügbar
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Inferenz durchführen
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
            
            # Ergebnisse verarbeiten
            probs = probs.cpu().numpy()[0]
            category_scores = dict(zip(self.categories, probs))
            
            # NSFW-Entscheidung treffen
            max_score = max(probs)
            is_nsfw = max_score > threshold
            
            return NSFWResult(
                is_nsfw=is_nsfw,
                confidence=float(max_score),
                categories=category_scores
            )
            
        except Exception as e:
            logger.error(f"Fehler bei der NSFW-Analyse: {str(e)}")
            return NSFWResult(
                is_nsfw=False,
                confidence=0.0,
                categories={},
                error=str(e)
            )

    def analyze_batch(self, images: List[bytes], threshold: float = 0.5) -> List[NSFWResult]:
        try:
            results = []
            for image_data in images:
                result = self.analyze_image(image_data, threshold)
                results.append(result)
            return results
        except Exception as e:
            logger.error(f"Fehler bei der Batch-Analyse: {str(e)}")
            raise

# Service-Instanz erstellen
nsfw_service = CLIPNSFWService()

@app.get("/health")
async def health_check():
    """Überprüft den Service-Status."""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "device": device
    }

@app.post("/analyze", response_model=NSFWResult)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analysiert ein Bild auf NSFW-Inhalte
    """
    try:
        return nsfw_service.analyze_image(
            request.image_data,
            request.threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/batch", response_model=List[NSFWResult])
async def analyze_batch(request: ImageAnalysisRequest):
    """
    Analysiert mehrere Bilder auf NSFW-Inhalte
    """
    try:
        return nsfw_service.analyze_batch(
            [request.image_data],
            request.threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
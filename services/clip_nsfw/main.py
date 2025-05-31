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

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Umgebungsvariablen laden
load_dotenv()

# FastAPI App initialisieren
app = FastAPI(title="CLIP NSFW Detection Service")

# CLIP Modell und Vorverarbeitung laden
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# NSFW-Kategorien
NSFW_CATEGORIES = [
    "nude", "explicit", "sexual", "violence", "gore",
    "safe", "appropriate", "family-friendly"
]

class NSFWResult(BaseModel):
    category: str
    confidence: float
    is_nsfw: bool

class AnalysisResponse(BaseModel):
    results: List[NSFWResult]
    processing_time: float
    device: str

@app.get("/health")
async def health_check():
    """Überprüft den Service-Status."""
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "device": device
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analysiert ein Bild auf NSFW-Inhalte.
    
    Args:
        file: Hochgeladenes Bild
        
    Returns:
        AnalysisResponse mit NSFW-Analyseergebnissen
    """
    try:
        # Bild laden und vorverarbeiten
        image = Image.open(file.file)
        image_input = preprocess(image).unsqueeze(0).to(device)
        
        # Text-Embeddings für NSFW-Kategorien
        text_inputs = torch.cat([clip.tokenize(cat) for cat in NSFW_CATEGORIES]).to(device)
        
        # Inferenz durchführen
        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_inputs)
            
            # Normalisierung
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)
            
            # Ähnlichkeiten berechnen
            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            
        # Ergebnisse formatieren
        results = []
        for i, category in enumerate(NSFW_CATEGORIES):
            confidence = float(similarity[0][i])
            is_nsfw = category not in ["safe", "appropriate", "family-friendly"]
            
            results.append(NSFWResult(
                category=category,
                confidence=confidence,
                is_nsfw=is_nsfw
            ))
        
        return AnalysisResponse(
            results=results,
            processing_time=0.0,  # TODO: Implementieren
            device=device
        )
        
    except Exception as e:
        logger.error(f"Fehler bei der Bildanalyse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_analyze")
async def batch_analyze(files: List[UploadFile] = File(...)):
    """
    Analysiert mehrere Bilder in einem Batch.
    
    Args:
        files: Liste von hochgeladenen Bildern
        
    Returns:
        Liste von AnalysisResponse-Objekten
    """
    results = []
    for file in files:
        result = await analyze_image(file)
        results.append(result)
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
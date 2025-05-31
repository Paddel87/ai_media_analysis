from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
import logging
from typing import List, Dict, Optional
import os

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ocr_service")

app = FastAPI(
    title="OCR and Logo Detection Service",
    description="Service für Texterkennung und Logo-Erkennung in Bildern und Videos"
)

class ImageAnalysisRequest(BaseModel):
    image_data: bytes
    detect_text: bool = True
    detect_logos: bool = True
    language: str = "deu+eng"

class AnalysisResult(BaseModel):
    text_results: Optional[List[Dict[str, any]]] = None
    logo_results: Optional[List[Dict[str, any]]] = None
    error: Optional[str] = None

class OCRService:
    def __init__(self):
        self.logo_processor = None
        self.logo_model = None
        self.initialize_models()
        
    def initialize_models(self):
        try:
            # Logo-Erkennungsmodell initialisieren
            model_name = "microsoft/resnet-50"
            self.logo_processor = AutoImageProcessor.from_pretrained(model_name)
            self.logo_model = AutoModelForImageClassification.from_pretrained(model_name)
            logger.info("Logo-Erkennungsmodell erfolgreich initialisiert")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Modelle: {str(e)}")
            raise

    def analyze_image(self, image_data: bytes, detect_text: bool = True, 
                     detect_logos: bool = True, language: str = "deu+eng") -> AnalysisResult:
        try:
            # Bild in numpy array konvertieren
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            results = AnalysisResult()
            
            if detect_text:
                # OCR durchführen
                text_results = self.perform_ocr(image, language)
                results.text_results = text_results
                
            if detect_logos:
                # Logo-Erkennung durchführen
                logo_results = self.detect_logos(image)
                results.logo_results = logo_results
                
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Bildanalyse: {str(e)}")
            return AnalysisResult(error=str(e))

    def perform_ocr(self, image: np.ndarray, language: str) -> List[Dict[str, any]]:
        try:
            # Bild für OCR vorbereiten
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # OCR durchführen
            text = pytesseract.image_to_data(pil_image, lang=language, output_type=pytesseract.Output.DICT)
            
            # Ergebnisse formatieren
            results = []
            for i in range(len(text['text'])):
                if text['text'][i].strip():
                    results.append({
                        'text': text['text'][i],
                        'confidence': float(text['conf'][i]) / 100.0,
                        'bbox': {
                            'x': text['left'][i],
                            'y': text['top'][i],
                            'width': text['width'][i],
                            'height': text['height'][i]
                        }
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der OCR: {str(e)}")
            raise

    def detect_logos(self, image: np.ndarray) -> List[Dict[str, any]]:
        try:
            # Bild für Logo-Erkennung vorbereiten
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            inputs = self.logo_processor(pil_image, return_tensors="pt")
            
            # Logo-Erkennung durchführen
            with torch.no_grad():
                outputs = self.logo_model(**inputs)
                predictions = outputs.logits.softmax(dim=1)
                
            # Top-5 Vorhersagen extrahieren
            top5_prob, top5_indices = torch.topk(predictions[0], 5)
            
            results = []
            for prob, idx in zip(top5_prob, top5_indices):
                results.append({
                    'label': self.logo_model.config.id2label[idx.item()],
                    'confidence': float(prob.item())
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Logo-Erkennung: {str(e)}")
            raise

# Service-Instanz erstellen
ocr_service = OCRService()

@app.post("/analyze", response_model=AnalysisResult)
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analysiert ein Bild auf Text und Logos
    """
    try:
        return ocr_service.analyze_image(
            request.image_data,
            request.detect_text,
            request.detect_logos,
            request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
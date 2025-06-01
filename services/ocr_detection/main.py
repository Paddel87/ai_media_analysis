import cv2
import numpy as np
import easyocr
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from typing import List, Dict, Optional
import logging
from pydantic import BaseModel
import torch

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="OCR Detection Service")

# OCR Reader initialisieren
device = "cuda" if torch.cuda.is_available() else "cpu"
reader = easyocr.Reader(["de", "en"], gpu=torch.cuda.is_available())


class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: List[List[float]]
    language: str


class OCRResponse(BaseModel):
    results: List[OCRResult]
    processing_time: float
    image_size: Dict[str, int]


@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    try:
        # Bild einlesen
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JSONResponse(
                status_code=400, content={"error": "Ungültiges Bildformat"}
            )

        # OCR durchführen
        results = reader.readtext(img)

        # Ergebnisse formatieren
        ocr_results = []
        for bbox, text, confidence in results:
            ocr_result = OCRResult(
                text=text,
                confidence=float(confidence),
                bbox=bbox,
                language="de" if any(c.isalpha() for c in text) else "unknown",
            )
            ocr_results.append(ocr_result)

        # Response erstellen
        response = OCRResponse(
            results=ocr_results,
            processing_time=0.0,  # TODO: Implementieren
            image_size={"width": img.shape[1], "height": img.shape[0]},
        )

        return response

    except Exception as e:
        logger.error(f"Fehler bei der OCR-Analyse: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/health")
async def health_check():
    return {"status": "healthy", "device": device}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

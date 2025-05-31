from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import whisper
import torch
import numpy as np
import logging
from typing import Optional, List, Dict
import os
from datetime import datetime
import json
import tempfile
import uuid

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whisper_transcriber_service")

app = FastAPI(
    title="Whisper Transkription Service",
    description="Service für Audio-Transkription mit OpenAI Whisper"
)

class TranscriptionRequest(BaseModel):
    job_id: str
    media_id: str
    source_type: str
    language: Optional[str] = None
    model_size: str = "base"
    task: str = "transcribe"

class TranscriptionResult(BaseModel):
    text: str
    segments: List[Dict]
    language: str
    job_id: str
    media_id: str
    source_type: str
    timestamp: str

class WhisperService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.model_sizes = ["tiny", "base", "small", "medium", "large"]
        
    def load_model(self, model_size: str) -> whisper.Whisper:
        """
        Lädt das Whisper-Modell der angegebenen Größe
        """
        if model_size not in self.model_sizes:
            raise ValueError(f"Ungültige Modellgröße. Verfügbar: {self.model_sizes}")
            
        if model_size not in self.models:
            logger.info(f"Lade Whisper Modell: {model_size}")
            self.models[model_size] = whisper.load_model(
                model_size,
                device=self.device
            )
            
        return self.models[model_size]
        
    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        model_size: str = "base",
        task: str = "transcribe"
    ) -> Dict:
        """
        Transkribiert eine Audiodatei
        """
        try:
            # Modell laden
            model = self.load_model(model_size)
            
            # Transkription durchführen
            result = model.transcribe(
                audio_path,
                language=language,
                task=task
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Transkription: {str(e)}")
            raise

# Service-Instanz erstellen
whisper_service = WhisperService()

@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    request: TranscriptionRequest = None
):
    """
    Transkribiert eine Audiodatei
    """
    try:
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
            
        # Transkription durchführen
        result = await whisper_service.transcribe_audio(
            temp_path,
            language=request.language if request else None,
            model_size=request.model_size if request else "base",
            task=request.task if request else "transcribe"
        )
        
        # Temporäre Datei löschen
        os.unlink(temp_path)
        
        # Ergebnis formatieren
        response = TranscriptionResult(
            text=result["text"],
            segments=result["segments"],
            language=result["language"],
            job_id=request.job_id if request else str(uuid.uuid4()),
            media_id=request.media_id if request else str(uuid.uuid4()),
            source_type=request.source_type if request else "audio",
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # Teste GPU-Verfügbarkeit
        gpu_available = torch.cuda.is_available()
        
        # Teste Modell-Ladung
        model_loaded = "base" in whisper_service.models
        
        return {
            "status": "healthy",
            "gpu_available": gpu_available,
            "model_loaded": model_loaded
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
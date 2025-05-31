from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
import whisper
import torch
import numpy as np
import logging
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
import json
import tempfile
import uuid
import ffmpeg
import asyncio
from concurrent.futures import ThreadPoolExecutor
import redis
import pickle
from functools import lru_cache
import soundfile as sf
import librosa
import aiofiles
import aiohttp
from pathlib import Path

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whisper_transcriber_service")

app = FastAPI(
    title="Whisper Transkription Service",
    description="Service für Audio-Transkription mit OpenAI Whisper"
)

# Redis-Konfiguration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Thread Pool für CPU-intensive Operationen
thread_pool = ThreadPoolExecutor(max_workers=4)

class TranscriptionRequest(BaseModel):
    job_id: str
    media_id: str
    source_type: str
    language: Optional[str] = None
    model_size: str = "base"
    task: str = "transcribe"
    no_censorship: bool = True
    batch_size: int = 1

class BatchTranscriptionRequest(BaseModel):
    files: List[TranscriptionRequest]
    batch_size: int = 4

class TranscriptionResult(BaseModel):
    text: str
    segments: List[Dict]
    language: str
    job_id: str
    media_id: str
    source_type: str
    timestamp: str
    duration: float
    word_timestamps: Optional[List[Dict]] = None

class WhisperService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.model_sizes = ["tiny", "base", "small", "medium", "large"]
        self.supported_formats = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".avi", ".mkv"]
        
        # Redis-Verbindung
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
    @lru_cache(maxsize=5)
    def load_model(self, model_size: str) -> whisper.Whisper:
        """
        Lädt das Whisper-Modell der angegebenen Größe mit Caching
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
        
    async def preprocess_audio(self, audio_path: str) -> str:
        """
        Vorverarbeitung der Audiodatei
        """
        try:
            # Prüfe Dateiformat
            file_ext = os.path.splitext(audio_path)[1].lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"Nicht unterstütztes Dateiformat: {file_ext}")
            
            # Konvertiere zu WAV wenn nötig
            if file_ext != ".wav":
                output_path = audio_path + ".wav"
                stream = ffmpeg.input(audio_path)
                stream = ffmpeg.output(stream, output_path, acodec="pcm_s16le", ac=1, ar=16000)
                ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)
                return output_path
            
            return audio_path
            
        except Exception as e:
            logger.error(f"Fehler bei der Audio-Vorverarbeitung: {str(e)}")
            raise

    async def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        model_size: str = "base",
        task: str = "transcribe",
        no_censorship: bool = True
    ) -> Dict:
        """
        Transkribiert eine Audiodatei
        """
        try:
            # Cache-Key generieren
            cache_key = f"transcription:{hash(audio_path)}:{model_size}:{language}:{task}"
            
            # Prüfe Cache
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)
            
            # Modell laden
            model = self.load_model(model_size)
            
            # Audio vorverarbeiten
            processed_audio_path = await self.preprocess_audio(audio_path)
            
            # Transkription durchführen
            result = model.transcribe(
                processed_audio_path,
                language=language,
                task=task,
                fp16=torch.cuda.is_available(),
                verbose=False
            )
            
            # Zensur entfernen wenn gewünscht
            if no_censorship:
                result = self._remove_censorship(result)
            
            # Wort-Timestamps hinzufügen
            result["word_timestamps"] = self._extract_word_timestamps(result["segments"])
            
            # Dauer hinzufügen
            result["duration"] = self._get_audio_duration(processed_audio_path)
            
            # In Cache speichern
            self.redis_client.set(cache_key, pickle.dumps(result))
            
            # Temporäre Datei löschen
            if processed_audio_path != audio_path:
                os.unlink(processed_audio_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Transkription: {str(e)}")
            raise

    def _remove_censorship(self, result: Dict) -> Dict:
        """
        Entfernt Zensur aus der Transkription
        """
        try:
            # Liste von Zensur-Mustern
            censorship_patterns = [
                "[*]", "[bleep]", "[beep]", "[censored]",
                "***", "****", "*****", "[REDACTED]"
            ]
            
            # Text bereinigen
            text = result["text"]
            for pattern in censorship_patterns:
                text = text.replace(pattern, "")
            
            # Segmente bereinigen
            for segment in result["segments"]:
                segment_text = segment["text"]
                for pattern in censorship_patterns:
                    segment_text = segment_text.replace(pattern, "")
                segment["text"] = segment_text
            
            result["text"] = text
            return result
            
        except Exception as e:
            logger.error(f"Fehler beim Entfernen der Zensur: {str(e)}")
            return result

    def _extract_word_timestamps(self, segments: List[Dict]) -> List[Dict]:
        """
        Extrahiert Wort-Timestamps aus den Segmenten
        """
        try:
            word_timestamps = []
            for segment in segments:
                words = segment["text"].split()
                if "words" in segment:
                    for word in segment["words"]:
                        word_timestamps.append({
                            "word": word["word"],
                            "start": word["start"],
                            "end": word["end"],
                            "confidence": word.get("confidence", 0.0)
                        })
            return word_timestamps
            
        except Exception as e:
            logger.error(f"Fehler beim Extrahieren der Wort-Timestamps: {str(e)}")
            return []

    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Ermittelt die Dauer der Audiodatei
        """
        try:
            return librosa.get_duration(path=audio_path)
        except Exception as e:
            logger.error(f"Fehler beim Ermitteln der Audiodauer: {str(e)}")
            return 0.0

    async def process_batch(self, batch: List[TranscriptionRequest]) -> List[Dict]:
        """
        Verarbeitet einen Batch von Audiodateien
        """
        try:
            results = []
            for request in batch:
                result = await self.transcribe_audio(
                    request.audio_path,
                    language=request.language,
                    model_size=request.model_size,
                    task=request.task,
                    no_censorship=request.no_censorship
                )
                results.append(result)
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {str(e)}")
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
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            await temp_file.write(content)
            temp_path = temp_file.name
            
        # Transkription durchführen
        result = await whisper_service.transcribe_audio(
            temp_path,
            language=request.language if request else None,
            model_size=request.model_size if request else "base",
            task=request.task if request else "transcribe",
            no_censorship=request.no_censorship if request else True
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
            timestamp=datetime.utcnow().isoformat(),
            duration=result["duration"],
            word_timestamps=result.get("word_timestamps", [])
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe_batch")
async def transcribe_batch(request: BatchTranscriptionRequest):
    """
    Transkribiert einen Batch von Audiodateien
    """
    try:
        # Batch in Chunks aufteilen
        chunks = [request.files[i:i + request.batch_size] 
                 for i in range(0, len(request.files), request.batch_size)]
        
        results = []
        for chunk in chunks:
            chunk_results = await whisper_service.process_batch(chunk)
            results.extend(chunk_results)
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # GPU-Verfügbarkeit prüfen
        gpu_available = torch.cuda.is_available()
        
        # Modell-Ladung prüfen
        model_loaded = "base" in whisper_service.models
        
        # Redis-Verbindung prüfen
        redis_healthy = whisper_service.redis_client.ping()
        
        return {
            "status": "healthy" if all([gpu_available, model_loaded, redis_healthy]) else "unhealthy",
            "gpu_available": gpu_available,
            "model_loaded": model_loaded,
            "redis": "available" if redis_healthy else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
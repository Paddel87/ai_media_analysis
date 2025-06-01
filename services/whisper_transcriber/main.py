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
import gc

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whisper_transcriber_service")

app = FastAPI(
    title="Whisper Transkription Service",
    description="Service für Audio-Transkription mit OpenAI Whisper",
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
    def __init__(
        self,
        model_name: str = "base",
        cache_dir: str = "data/whisper_cache",
        redis_host: str = "redis",
        redis_port: int = 6379,
        redis_db: int = 0,
        batch_size: int = 4,
        gpu_memory_threshold: float = 0.8,
        cache_ttl: int = 3600,
    ):
        """
        Initialisiert den Whisper-Service mit Performance-Optimierungen.

        Args:
            model_name: Name des zu ladenden Modells
            cache_dir: Verzeichnis für Modell-Cache
            redis_host: Redis-Host
            redis_port: Redis-Port
            redis_db: Redis-Datenbank
            batch_size: Optimale Batch-Größe für GPU
            gpu_memory_threshold: GPU-Speicher-Schwellenwert
            cache_ttl: Cache-TTL in Sekunden
        """
        try:
            # Konfiguration
            self.model_name = model_name
            self.cache_dir = Path(cache_dir)
            self.batch_size = batch_size
            self.gpu_memory_threshold = gpu_memory_threshold
            self.cache_ttl = cache_ttl

            # Verzeichnis erstellen
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Redis für Caching
            self.redis_client = redis.Redis(
                host=redis_host, port=redis_port, db=redis_db, decode_responses=True
            )

            # CUDA-Optimierungen
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                self.device = torch.device("cuda")
            else:
                self.device = torch.device("cpu")

            # Modell laden
            self._load_model()

            logger.info(
                "Whisper-Service initialisiert",
                extra={
                    "model_name": model_name,
                    "batch_size": batch_size,
                    "device": str(self.device),
                },
            )

        except Exception as e:
            logger.error(
                "Fehler bei der Initialisierung des Whisper-Services", exc_info=True
            )
            raise

    def _load_model(self):
        """Lädt das Whisper-Modell."""
        try:
            # Modell laden
            self.model = whisper.load_model(
                self.model_name, device=self.device, download_root=self.cache_dir
            )

            logger.info("Whisper-Modell geladen")

        except Exception as e:
            logger.error("Fehler beim Laden des Whisper-Modells", exc_info=True)
            raise

    def _adjust_batch_size(self):
        """Passt die Batch-Größe basierend auf GPU-Speicher an."""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated()
            memory_reserved = torch.cuda.memory_reserved()
            total_memory = torch.cuda.get_device_properties(0).total_memory

            memory_usage = (memory_allocated + memory_reserved) / total_memory

            if memory_usage > self.gpu_memory_threshold:
                self.batch_size = max(1, self.batch_size // 2)
                logger.warning(
                    "Batch-Größe reduziert",
                    extra={
                        "new_batch_size": self.batch_size,
                        "memory_usage": memory_usage,
                    },
                )
            elif memory_usage < self.gpu_memory_threshold * 0.5:
                self.batch_size = min(32, self.batch_size * 2)
                logger.info(
                    "Batch-Größe erhöht",
                    extra={
                        "new_batch_size": self.batch_size,
                        "memory_usage": memory_usage,
                    },
                )

    def _cleanup_gpu_memory(self):
        """Bereinigt GPU-Speicher."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    async def transcribe_audio(
        self, audio_path: str, language: Optional[str] = None, task: str = "transcribe"
    ) -> Dict[str, Any]:
        """
        Transkribiert eine Audiodatei.

        Args:
            audio_path: Pfad zur Audiodatei
            language: Sprache (optional)
            task: Aufgabe (transcribe oder translate)

        Returns:
            Transkriptionsergebnisse
        """
        try:
            # Cache-Key generieren
            cache_key = f"transcribe:{hash(audio_path)}:{language}:{task}"

            # Cache prüfen
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)

            # Audio laden und transkribieren
            result = self.model.transcribe(audio_path, language=language, task=task)

            # Cache speichern
            self.redis_client.setex(cache_key, self.cache_ttl, pickle.dumps(result))

            # Batch-Größe anpassen
            self._adjust_batch_size()

            # GPU-Speicher bereinigen
            self._cleanup_gpu_memory()

            return result

        except Exception as e:
            logger.error("Fehler bei der Audio-Transkription", exc_info=True)
            raise

    async def transcribe_audio_batch(
        self,
        audio_paths: List[str],
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> List[Dict[str, Any]]:
        """
        Transkribiert mehrere Audiodateien in einem Batch.

        Args:
            audio_paths: Liste von Audio-Pfaden
            language: Sprache (optional)
            task: Aufgabe (transcribe oder translate)

        Returns:
            Liste von Transkriptionsergebnissen
        """
        try:
            results = []

            # Audiodateien in Batches aufteilen
            for i in range(0, len(audio_paths), self.batch_size):
                batch_paths = audio_paths[i : i + self.batch_size]

                # Batch verarbeiten
                batch_results = await asyncio.gather(
                    *[
                        self.transcribe_audio(audio_path, language, task)
                        for audio_path in batch_paths
                    ]
                )

                results.extend(batch_results)

                # Batch-Größe anpassen
                self._adjust_batch_size()

                # GPU-Speicher bereinigen
                self._cleanup_gpu_memory()

            return results

        except Exception as e:
            logger.error("Fehler bei der Batch-Audio-Transkription", exc_info=True)
            raise

    async def detect_language(self, audio_path: str) -> str:
        """
        Erkennt die Sprache einer Audiodatei.

        Args:
            audio_path: Pfad zur Audiodatei

        Returns:
            Erkannte Sprache
        """
        try:
            # Cache-Key generieren
            cache_key = f"detect_language:{hash(audio_path)}"

            # Cache prüfen
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)

            # Sprache erkennen
            result = self.model.transcribe(audio_path, task="transcribe", language=None)

            language = result["language"]

            # Cache speichern
            self.redis_client.setex(cache_key, self.cache_ttl, pickle.dumps(language))

            return language

        except Exception as e:
            logger.error("Fehler bei der Spracherkennung", exc_info=True)
            raise


# Service-Instanz erstellen
whisper_service = WhisperService()


@app.post("/transcribe")
async def transcribe_audio(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transkribiert eine Audiodatei.
    """
    try:
        result = await whisper_service.transcribe_audio(
            audio_path=request["audio_path"],
            language=request.get("language"),
            task=request.get("task", "transcribe"),
        )
        return result
    except Exception as e:
        logger.error("Fehler bei der Audio-Transkription", exc_info=True)
        raise


@app.post("/transcribe_batch")
async def transcribe_audio_batch(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transkribiert mehrere Audiodateien in einem Batch.
    """
    try:
        results = await whisper_service.transcribe_audio_batch(
            audio_paths=request["audio_paths"],
            language=request.get("language"),
            task=request.get("task", "transcribe"),
        )
        return {"results": results}
    except Exception as e:
        logger.error("Fehler bei der Batch-Audio-Transkription", exc_info=True)
        raise


@app.post("/detect_language")
async def detect_language(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Erkennt die Sprache einer Audiodatei.
    """
    try:
        language = await whisper_service.detect_language(request["audio_path"])
        return {"language": language}
    except Exception as e:
        logger.error("Fehler bei der Spracherkennung", exc_info=True)
        raise


@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # GPU-Verfügbarkeit prüfen
        gpu_available = torch.cuda.is_available()

        # Modell-Ladung prüfen
        model_loaded = "base" in whisper_service.model

        # Redis-Verbindung prüfen
        redis_healthy = whisper_service.redis_client.ping()

        return {
            "status": (
                "healthy"
                if all([gpu_available, model_loaded, redis_healthy])
                else "unhealthy"
            ),
            "gpu_available": gpu_available,
            "model_loaded": model_loaded,
            "redis": "available" if redis_healthy else "unavailable",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

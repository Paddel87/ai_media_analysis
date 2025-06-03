"""
LLM Service für AI Media Analysis System
Bietet verschiedene LLM-Provider (OpenAI, Claude, Gemini) für Textanalyse
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

import redis
from fastapi import FastAPI
from pydantic import BaseModel

import gc
import json
import pickle
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import aiohttp
import google.generativeai as genai
import numpy as np
import openai
import torch
from anthropic import Anthropic
from fastapi import BackgroundTasks, FastAPI, HTTPException
from langchain.chains import LLMChain
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential
from transformers import AutoModelForCausalLM, AutoTokenizer

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")

app = FastAPI(
    title="LLM Service",
    description="Service für verschiedene LLM-Anbieter und lokale Modelle",
)

# Redis-Konfiguration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Thread Pool für CPU-intensive Operationen
thread_pool = ThreadPoolExecutor(max_workers=4)


class LLMRequest(BaseModel):
    prompt: str
    provider: str = "gemini"  # gemini, openai, anthropic, local
    model: str = "gemini-pro"  # gemini-pro, gpt-4, claude-3-opus, mistral-7b, etc.
    temperature: float = 0.7
    max_tokens: int = 1000
    safety_settings: Optional[Dict] = None
    system_prompt: Optional[str] = None
    stream: bool = False


class LLMResponse(BaseModel):
    text: str
    provider: str
    model: str
    usage: Optional[Dict] = None
    safety_ratings: Optional[Dict] = None


class LLMService:
    def __init__(
        self,
        model_name: str = "gpt2",
        cache_dir: str = "data/llm_cache",
        redis_host: str = "redis",
        redis_port: int = 6379,
        redis_db: int = 0,
        batch_size: int = 4,
        max_length: int = 512,
        gpu_memory_threshold: float = 0.8,
        cache_ttl: int = 3600,
    ):
        """
        Initialisiert den LLM-Service mit Performance-Optimierungen.

        Args:
            model_name: Name des zu ladenden Modells
            cache_dir: Verzeichnis für Modell-Cache
            redis_host: Redis-Host
            redis_port: Redis-Port
            redis_db: Redis-Datenbank
            batch_size: Optimale Batch-Größe für GPU
            max_length: Maximale Sequenzlänge
            gpu_memory_threshold: GPU-Speicher-Schwellenwert
            cache_ttl: Cache-TTL in Sekunden
        """
        try:
            # Konfiguration
            self.model_name = model_name
            self.cache_dir = Path(cache_dir)
            self.batch_size = batch_size
            self.max_length = max_length
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

            # Modell und Tokenizer laden
            self._load_model()

            logger.info(
                "LLM-Service initialisiert",
                extra={
                    "model_name": model_name,
                    "batch_size": batch_size,
                    "device": str(self.device),
                },
            )

        except Exception as e:
            logger.error(
                "Fehler bei der Initialisierung des LLM-Services", exc_info=True
            )
            raise

    def _load_model(self):
        """Lädt das Modell und den Tokenizer."""
        try:
            # Tokenizer laden
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, cache_dir=self.cache_dir
            )

            # Modell laden
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                cache_dir=self.cache_dir,
                torch_dtype=(
                    torch.float16 if torch.cuda.is_available() else torch.float32
                ),
            )

            # Modell auf GPU verschieben
            if torch.cuda.is_available():
                self.model = self.model.to(self.device)

            logger.info("Modell und Tokenizer geladen")

        except Exception as e:
            logger.error("Fehler beim Laden des Modells", exc_info=True)
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

    async def generate_text(
        self,
        prompt: str,
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        num_return_sequences: int = 1,
    ) -> List[str]:
        """
        Generiert Text basierend auf einem Prompt.

        Args:
            prompt: Eingabetext
            max_length: Maximale Ausgabelänge
            temperature: Temperatur für Sampling
            top_p: Top-p für Nucleus Sampling
            top_k: Top-k für Sampling
            num_return_sequences: Anzahl der zurückzugebenden Sequenzen

        Returns:
            Liste generierter Texte
        """
        try:
            # Cache-Key generieren
            cache_key = f"generate:{hash(prompt)}:{max_length}:{temperature}:{top_p}:{top_k}:{num_return_sequences}"

            # Cache prüfen
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)

            # Parameter anpassen
            max_length = max_length or self.max_length

            # Text tokenisieren
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=max_length,
            )

            # Eingaben auf GPU verschieben
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Text generieren
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    num_return_sequences=num_return_sequences,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            # Text dekodieren
            generated_texts = [
                self.tokenizer.decode(output, skip_special_tokens=True)
                for output in outputs
            ]

            # Cache speichern
            self.redis_client.setex(
                cache_key, self.cache_ttl, pickle.dumps(generated_texts)
            )

            # Batch-Größe anpassen
            self._adjust_batch_size()

            # GPU-Speicher bereinigen
            self._cleanup_gpu_memory()

            return generated_texts

        except Exception as e:
            logger.error("Fehler bei der Textgenerierung", exc_info=True)
            raise

    async def generate_text_batch(
        self,
        prompts: List[str],
        max_length: Optional[int] = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        num_return_sequences: int = 1,
    ) -> List[List[str]]:
        """
        Generiert Text für mehrere Prompts in einem Batch.

        Args:
            prompts: Liste von Eingabetexten
            max_length: Maximale Ausgabelänge
            temperature: Temperatur für Sampling
            top_p: Top-p für Nucleus Sampling
            top_k: Top-k für Sampling
            num_return_sequences: Anzahl der zurückzugebenden Sequenzen

        Returns:
            Liste von Listen generierter Texte
        """
        try:
            results = []

            # Prompts in Batches aufteilen
            for i in range(0, len(prompts), self.batch_size):
                batch_prompts = prompts[i : i + self.batch_size]

                # Batch verarbeiten
                batch_results = await asyncio.gather(
                    *[
                        self.generate_text(
                            prompt,
                            max_length,
                            temperature,
                            top_p,
                            top_k,
                            num_return_sequences,
                        )
                        for prompt in batch_prompts
                    ]
                )

                results.extend(batch_results)

                # Batch-Größe anpassen
                self._adjust_batch_size()

                # GPU-Speicher bereinigen
                self._cleanup_gpu_memory()

            return results

        except Exception as e:
            logger.error("Fehler bei der Batch-Textgenerierung", exc_info=True)
            raise

    async def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Berechnet Embeddings für eine Liste von Texten.

        Args:
            texts: Liste von Texten

        Returns:
            NumPy-Array mit Embeddings
        """
        try:
            # Cache-Key generieren
            cache_key = f"embeddings:{hash(str(texts))}"

            # Cache prüfen
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)

            # Texte tokenisieren
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length,
            )

            # Eingaben auf GPU verschieben
            if torch.cuda.is_available():
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Embeddings berechnen
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                embeddings = outputs.hidden_states[-1].mean(dim=1).cpu().numpy()

            # Cache speichern
            self.redis_client.setex(cache_key, self.cache_ttl, pickle.dumps(embeddings))

            # Batch-Größe anpassen
            self._adjust_batch_size()

            # GPU-Speicher bereinigen
            self._cleanup_gpu_memory()

            return embeddings

        except Exception as e:
            logger.error("Fehler bei der Embedding-Berechnung", exc_info=True)
            raise


# Service-Instanz erstellen
llm_service = LLMService()


@app.post("/generate")
async def generate_text(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generiert Text basierend auf einem Prompt.
    """
    try:
        texts = await llm_service.generate_text(
            prompt=request["prompt"],
            max_length=request.get("max_length"),
            temperature=request.get("temperature", 0.7),
            top_p=request.get("top_p", 0.9),
            top_k=request.get("top_k", 50),
            num_return_sequences=request.get("num_return_sequences", 1),
        )
        return {"texts": texts}
    except Exception as e:
        logger.error("Fehler bei der Textgenerierung", exc_info=True)
        raise


@app.post("/generate_batch")
async def generate_text_batch(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generiert Text für mehrere Prompts in einem Batch.
    """
    try:
        texts = await llm_service.generate_text_batch(
            prompts=request["prompts"],
            max_length=request.get("max_length"),
            temperature=request.get("temperature", 0.7),
            top_p=request.get("top_p", 0.9),
            top_k=request.get("top_k", 50),
            num_return_sequences=request.get("num_return_sequences", 1),
        )
        return {"texts": texts}
    except Exception as e:
        logger.error("Fehler bei der Batch-Textgenerierung", exc_info=True)
        raise


@app.post("/embeddings")
async def get_embeddings(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Berechnet Embeddings für eine Liste von Texten.
    """
    try:
        embeddings = await llm_service.get_embeddings(request["texts"])
        return {"embeddings": embeddings.tolist()}
    except Exception as e:
        logger.error("Fehler bei der Embedding-Berechnung", exc_info=True)
        raise


@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # Redis-Verbindung testen
        redis_healthy = llm_service.redis_client.ping()

        # Verfügbare Modelle prüfen
        available_models = {
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "local": list(llm_service.model_name),
        }

        return {
            "status": "healthy" if redis_healthy else "unhealthy",
            "redis": "available" if redis_healthy else "unavailable",
            "available_models": available_models,
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

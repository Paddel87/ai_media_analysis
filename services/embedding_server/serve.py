"""
Embedding Server - Vector Management Service
CPU-optimierter Embedding-Service für Text- und Medien-Embeddings
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# FastAPI App
app = FastAPI(
    title="Embedding Server",
    description="Vector Management Service für AI Media Analysis",
    version="1.0.0",
)

# Environment Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 3))
VECTOR_DB_HOST = os.getenv("VECTOR_DB_HOST", "vector-db")
VECTOR_DB_PORT = int(os.getenv("VECTOR_DB_PORT", 8000))
MODEL_TYPE = os.getenv("MODEL_TYPE", "cpu")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Global Variables
redis_client = None

# Logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger("embedding_server")


class EmbeddingRequest(BaseModel):
    text: Union[str, List[str]]
    model: Optional[str] = "sentence-transformers"
    normalize: bool = True


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimensions: int
    count: int


class VectorSearchRequest(BaseModel):
    query_embedding: List[float]
    top_k: int = 10
    threshold: Optional[float] = None


class VectorSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    count: int
    query_time_ms: float


async def init_redis():
    """Initialisiert Redis-Verbindung"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        # Test connection
        redis_client.ping()
        logger.info(f"Redis verbunden: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return True
    except Exception as e:
        logger.error(f"Redis Verbindungsfehler: {e}")
        redis_client = None
        return False


def generate_dummy_embedding(text: str, dimensions: int = 384) -> List[float]:
    """Generiert ein Dummy-Embedding basierend auf Text-Hash (für CPU-only Deployment)"""
    # Hash des Textes für reproduzierbare Embeddings
    text_hash = hashlib.sha256(text.encode()).hexdigest()

    # Konvertiere Hash zu Embedding
    embedding = []
    for i in range(0, dimensions * 8, 8):
        hex_chunk = text_hash[i % len(text_hash) : (i % len(text_hash)) + 8]
        if len(hex_chunk) < 8:
            hex_chunk += text_hash[: 8 - len(hex_chunk)]

        # Konvertiere zu Float zwischen -1 und 1
        int_val = int(hex_chunk, 16)
        float_val = (int_val / (16**8)) * 2 - 1
        embedding.append(float_val)

    # Normalisierung
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = [x / norm for x in embedding]

    return embedding[:dimensions]


@app.on_event("startup")
async def startup_event():
    """Startup Event Handler"""
    logger.info("Embedding Server startet...")

    # Redis initialisieren
    await init_redis()

    # Service-Status in Redis setzen
    if redis_client:
        service_info = {
            "service": "embedding_server",
            "status": "running",
            "model_type": MODEL_TYPE,
            "batch_size": BATCH_SIZE,
            "started_at": datetime.now().isoformat(),
        }
        redis_client.hset("system:embedding_server", mapping=service_info)

    logger.info("Embedding Server bereit")


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    redis_status = False
    if redis_client:
        try:
            redis_client.ping()
            redis_status = True
        except Exception:
            redis_status = False

    return {
        "status": "healthy" if redis_status else "degraded",
        "service": "embedding_server",
        "redis_connected": redis_status,
        "model_type": MODEL_TYPE,
        "batch_size": BATCH_SIZE,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """Erstellt Embeddings für Text(e)"""
    try:
        texts = request.text if isinstance(request.text, list) else [request.text]

        logger.info(f"Embedding-Request: {len(texts)} Texte")

        # Dummy-Embeddings generieren (CPU-optimiert)
        embeddings = []
        for text in texts:
            embedding = generate_dummy_embedding(text, dimensions=384)
            embeddings.append(embedding)

        # In Redis cachen (optional)
        if redis_client:
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                cache_key = f"embedding:{hashlib.sha256(text.encode()).hexdigest()}"
                redis_client.setex(cache_key, 3600, str(embedding))  # 1h TTL

        return EmbeddingResponse(
            embeddings=embeddings,
            model=request.model or "dummy-cpu-model",
            dimensions=len(embeddings[0]) if embeddings else 0,
            count=len(embeddings),
        )

    except Exception as e:
        logger.error(f"Embedding-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/embeddings/cached/{text_hash}")
async def get_cached_embedding(text_hash: str):
    """Ruft gecachte Embeddings ab"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis nicht verfügbar")

        cache_key = f"embedding:{text_hash}"
        cached_embedding = redis_client.get(cache_key)

        if cached_embedding:
            return {
                "embedding": eval(cached_embedding),  # TODO: Sicherer JSON-Parse
                "cached": True,
                "timestamp": datetime.now().isoformat(),
            }
        else:
            raise HTTPException(status_code=404, detail="Embedding nicht im Cache")

    except Exception as e:
        logger.error(f"Cache-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=VectorSearchResponse)
async def vector_search(request: VectorSearchRequest):
    """Vektor-Ähnlichkeitssuche"""
    try:
        start_time = datetime.now()

        # TODO: Integration mit Vector-DB Service
        # Für jetzt: Dummy-Ergebnisse
        dummy_results = [
            {
                "id": f"doc_{i}",
                "score": 0.95 - (i * 0.1),
                "metadata": {"type": "text", "source": f"document_{i}"},
            }
            for i in range(min(request.top_k, 5))
        ]

        query_time = (datetime.now() - start_time).total_seconds() * 1000

        return VectorSearchResponse(
            results=dummy_results, count=len(dummy_results), query_time_ms=query_time
        )

    except Exception as e:
        logger.error(f"Suche-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Service-Statistiken"""
    try:
        stats = {
            "service": "embedding_server",
            "model_type": MODEL_TYPE,
            "batch_size": BATCH_SIZE,
            "redis_connected": redis_client is not None,
            "uptime_seconds": 0,  # TODO: Implementieren
            "processed_requests": 0,  # TODO: Counter implementieren
            "cache_hits": 0,  # TODO: Redis Stats
            "timestamp": datetime.now().isoformat(),
        }

        if redis_client:
            try:
                # Redis-Info abrufen
                redis_info = redis_client.info()
                stats["redis_info"] = {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                }
            except Exception:
                pass

        return stats

    except Exception as e:
        logger.error(f"Stats-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Starting embedding server...")
    uvicorn.run("serve:app", host="0.0.0.0", port=8000, log_level=LOG_LEVEL.lower())

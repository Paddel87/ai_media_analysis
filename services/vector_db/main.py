from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import qdrant_client
from qdrant_client.http import models
import numpy as np
import logging
from typing import List, Dict, Optional, Union, Any
import os
from datetime import datetime
import json
import uuid
import redis
import pickle
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_db_service")

app = FastAPI(
    title="Vector DB Service",
    description="Service für Embedding-Speicherung und Ähnlichkeitssuche mit Qdrant"
)

# Redis-Konfiguration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Thread Pool für CPU-intensive Operationen
thread_pool = ThreadPoolExecutor(max_workers=4)

class Vector(BaseModel):
    id: str
    vector: List[float]
    metadata: Dict
    collection: str

class BatchVector(BaseModel):
    vectors: List[Vector]
    batch_size: int = 100

class SearchRequest(BaseModel):
    vector: List[float]
    collection: str
    limit: int = 10
    score_threshold: float = 0.7
    filter: Optional[Dict] = None
    search_params: Optional[Dict] = None
    with_payload: bool = True
    with_vectors: bool = False

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict
    vector: Optional[List[float]] = None

class CollectionConfig(BaseModel):
    name: str
    vector_size: int
    distance: str = "Cosine"
    on_disk_payload: bool = True
    optimizers_config: Optional[Dict] = None
    replication_factor: int = 1
    write_consistency_factor: int = 1
    init_from: Optional[Dict] = None
    quantization_config: Optional[Dict] = None

class VectorDBService:
    def __init__(self):
        self.client = qdrant_client.QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        self.collections = {}
        
        # Redis-Verbindung
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def create_collection(self, config: CollectionConfig) -> bool:
        """
        Erstellt eine neue Collection mit Retry-Logik
        """
        try:
            # Collection existiert bereits
            if config.name in self.collections:
                return True
                
            # Collection erstellen
            self.client.create_collection(
                collection_name=config.name,
                vectors_config=models.VectorParams(
                    size=config.vector_size,
                    distance=models.Distance.COSINE
                ),
                optimizers_config=config.optimizers_config,
                replication_factor=config.replication_factor,
                write_consistency_factor=config.write_consistency_factor,
                init_from=config.init_from,
                quantization_config=config.quantization_config
            )
            
            self.collections[config.name] = config
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Collection: {str(e)}")
            raise
            
    @lru_cache(maxsize=1000)
    def get_collection_info(self, collection_name: str) -> Dict:
        """
        Gibt Informationen über eine Collection zurück
        """
        try:
            return self.client.get_collection(collection_name=collection_name)
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Collection-Info: {str(e)}")
            raise

    async def upsert_vectors_batch(self, batch: BatchVector) -> bool:
        """
        Speichert oder aktualisiert mehrere Vektoren in einem Batch
        """
        try:
            # Collection existiert nicht
            collection_name = batch.vectors[0].collection
            if collection_name not in self.collections:
                raise ValueError(f"Collection {collection_name} existiert nicht")
                
            # Batch in Chunks aufteilen
            chunks = [batch.vectors[i:i + batch.batch_size] 
                     for i in range(0, len(batch.vectors), batch.batch_size)]
            
            for chunk in chunks:
                points = [
                    models.PointStruct(
                        id=vector.id,
                        vector=vector.vector,
                        payload=vector.metadata
                    )
                    for vector in chunk
                ]
                
                # Vektoren speichern
                self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )
                
                # Cache invalidieren
                self._invalidate_cache(collection_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Batch-Speichern der Vektoren: {str(e)}")
            raise
            
    def upsert_vector(self, vector: Vector) -> bool:
        """
        Speichert oder aktualisiert einen Vektor
        """
        try:
            # Collection existiert nicht
            if vector.collection not in self.collections:
                raise ValueError(f"Collection {vector.collection} existiert nicht")
                
            # Cache-Key generieren
            cache_key = f"vector:{vector.collection}:{vector.id}"
            
            # Vektor speichern
            self.client.upsert(
                collection_name=vector.collection,
                points=[
                    models.PointStruct(
                        id=vector.id,
                        vector=vector.vector,
                        payload=vector.metadata
                    )
                ]
            )
            
            # Cache aktualisieren
            self.redis_client.set(cache_key, pickle.dumps(vector))
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Vektors: {str(e)}")
            raise
            
    async def search_vectors(self, request: SearchRequest) -> List[SearchResult]:
        """
        Sucht ähnliche Vektoren
        """
        try:
            # Collection existiert nicht
            if request.collection not in self.collections:
                raise ValueError(f"Collection {request.collection} existiert nicht")
                
            # Cache-Key generieren
            cache_key = f"search:{request.collection}:{hash(str(request.dict()))}"
            
            # Cache prüfen
            cached_results = self.redis_client.get(cache_key)
            if cached_results:
                return pickle.loads(cached_results)
                
            # Suche durchführen
            results = self.client.search(
                collection_name=request.collection,
                query_vector=request.vector,
                limit=request.limit,
                score_threshold=request.score_threshold,
                query_filter=request.filter,
                search_params=request.search_params,
                with_payload=request.with_payload,
                with_vectors=request.with_vectors
            )
            
            # Ergebnisse formatieren
            formatted_results = [
                SearchResult(
                    id=str(point.id),
                    score=point.score,
                    metadata=point.payload,
                    vector=point.vector if request.with_vectors else None
                )
                for point in results
            ]
            
            # Cache speichern
            self.redis_client.set(cache_key, pickle.dumps(formatted_results))
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Fehler bei der Vektorsuche: {str(e)}")
            raise
            
    def delete_vector(self, collection: str, vector_id: str) -> bool:
        """
        Löscht einen Vektor
        """
        try:
            # Collection existiert nicht
            if collection not in self.collections:
                raise ValueError(f"Collection {collection} existiert nicht")
                
            # Vektor löschen
            self.client.delete(
                collection_name=collection,
                points_selector=models.PointIdsList(
                    points=[vector_id]
                )
            )
            
            # Cache invalidieren
            self._invalidate_cache(collection)
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Vektors: {str(e)}")
            raise
            
    def _invalidate_cache(self, collection: str):
        """
        Invalidiert den Cache für eine Collection
        """
        try:
            # Cache-Keys für Collection löschen
            pattern = f"*:{collection}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Fehler beim Invalidieren des Caches: {str(e)}")

# Service-Instanz erstellen
vector_db_service = VectorDBService()

@app.post("/collections")
async def create_collection(config: CollectionConfig):
    """
    Erstellt eine neue Collection
    """
    try:
        success = vector_db_service.create_collection(config)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}")
async def get_collection_info(collection_name: str):
    """
    Gibt Informationen über eine Collection zurück
    """
    try:
        info = vector_db_service.get_collection_info(collection_name)
        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vectors")
async def upsert_vector(vector: Vector):
    """
    Speichert oder aktualisiert einen Vektor
    """
    try:
        success = vector_db_service.upsert_vector(vector)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vectors/batch")
async def upsert_vectors_batch(batch: BatchVector):
    """
    Speichert oder aktualisiert mehrere Vektoren in einem Batch
    """
    try:
        success = await vector_db_service.upsert_vectors_batch(batch)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_vectors(request: SearchRequest):
    """
    Sucht ähnliche Vektoren
    """
    try:
        results = await vector_db_service.search_vectors(request)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vectors/{collection}/{vector_id}")
async def delete_vector(collection: str, vector_id: str):
    """
    Löscht einen Vektor
    """
    try:
        success = vector_db_service.delete_vector(collection, vector_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # Qdrant-Verbindung testen
        collections = vector_db_service.client.get_collections()
        
        # Redis-Verbindung testen
        redis_healthy = vector_db_service.redis_client.ping()
        
        return {
            "status": "healthy" if redis_healthy else "unhealthy",
            "collections": len(collections.collections),
            "qdrant_connected": True,
            "redis": "available" if redis_healthy else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import qdrant_client
from qdrant_client.http import models
import numpy as np
import logging
from typing import List, Dict, Optional, Union
import os
from datetime import datetime
import json
import uuid

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_db_service")

app = FastAPI(
    title="Vector DB Service",
    description="Service für Embedding-Speicherung und Ähnlichkeitssuche mit Qdrant"
)

class Vector(BaseModel):
    id: str
    vector: List[float]
    metadata: Dict
    collection: str

class SearchRequest(BaseModel):
    vector: List[float]
    collection: str
    limit: int = 10
    score_threshold: float = 0.7
    filter: Optional[Dict] = None

class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict

class CollectionConfig(BaseModel):
    name: str
    vector_size: int
    distance: str = "Cosine"

class VectorDBService:
    def __init__(self):
        self.client = qdrant_client.QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        self.collections = {}
        
    def create_collection(self, config: CollectionConfig) -> bool:
        """
        Erstellt eine neue Collection
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
                )
            )
            
            self.collections[config.name] = config
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Collection: {str(e)}")
            raise
            
    def upsert_vector(self, vector: Vector) -> bool:
        """
        Speichert oder aktualisiert einen Vektor
        """
        try:
            # Collection existiert nicht
            if vector.collection not in self.collections:
                raise ValueError(f"Collection {vector.collection} existiert nicht")
                
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
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Vektors: {str(e)}")
            raise
            
    def search_vectors(self, request: SearchRequest) -> List[SearchResult]:
        """
        Sucht ähnliche Vektoren
        """
        try:
            # Collection existiert nicht
            if request.collection not in self.collections:
                raise ValueError(f"Collection {request.collection} existiert nicht")
                
            # Suche durchführen
            results = self.client.search(
                collection_name=request.collection,
                query_vector=request.vector,
                limit=request.limit,
                score_threshold=request.score_threshold,
                query_filter=request.filter
            )
            
            # Ergebnisse formatieren
            return [
                SearchResult(
                    id=str(point.id),
                    score=point.score,
                    metadata=point.payload
                )
                for point in results
            ]
            
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
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen des Vektors: {str(e)}")
            raise

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

@app.post("/search")
async def search_vectors(request: SearchRequest):
    """
    Sucht ähnliche Vektoren
    """
    try:
        results = vector_db_service.search_vectors(request)
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
        
        return {
            "status": "healthy",
            "collections": len(collections.collections),
            "qdrant_connected": True
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
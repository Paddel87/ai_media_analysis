import gc
import logging
import os
import pickle
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False
    # Fallback für Development ohne FAISS
    class MockFaiss:
        @staticmethod
        def read_index(path: str) -> Any:
            return None
        @staticmethod
        def write_index(index: Any, path: str) -> None:
            pass
        @staticmethod
        def IndexFlatL2(dimension: int) -> Any:
            return None
        @staticmethod
        def GpuIndexFlatL2(resources: Any, dimension: int, config: Any) -> Any:
            return None
        @staticmethod
        def GpuIndexFlatConfig() -> Any:
            return None
        @staticmethod
        def StandardGpuResources() -> Any:
            return None

    faiss = MockFaiss()  # type: ignore

import numpy as np
import redis
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vector_db_service")

app = FastAPI(
    title="Vector DB Service",
    description="Service für Embedding-Speicherung und Ähnlichkeitssuche mit FAISS",
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
    metadata: Dict[str, Any]
    collection: str


class BatchVector(BaseModel):
    vectors: List[Vector]
    batch_size: int = 100


class SearchRequest(BaseModel):
    vector: List[float]
    collection: str
    limit: int = 10
    score_threshold: float = 0.7
    filter: Optional[Dict[str, Any]] = None
    search_params: Optional[Dict[str, Any]] = None
    with_payload: bool = True
    with_vectors: bool = False


class SearchResult(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


class CollectionConfig(BaseModel):
    name: str
    vector_size: int
    distance: str = "Cosine"
    on_disk_payload: bool = True
    optimizers_config: Optional[Dict[str, Any]] = None
    replication_factor: int = 1
    write_consistency_factor: int = 1
    init_from: Optional[Dict[str, Any]] = None
    quantization_config: Optional[Dict[str, Any]] = None


class CollectionInfo(BaseModel):
    name: str
    vector_count: int
    vector_size: int
    status: str
    indexed: bool


class VectorDB:
    def __init__(
        self,
        index_path: str = "data/vector_db",
        redis_host: str = "redis",
        redis_port: int = 6379,
        redis_db: int = 0,
        batch_size: int = 1000,
        gpu_memory_threshold: float = 0.8,
        cache_ttl: int = 3600,
    ):
        """
        Initialisiert die Vector DB mit Performance-Optimierungen.

        Args:
            index_path: Pfad zum Index-Verzeichnis
            redis_host: Redis-Host
            redis_port: Redis-Port
            redis_db: Redis-Datenbank
            batch_size: Optimale Batch-Größe für GPU
            gpu_memory_threshold: GPU-Speicher-Schwellenwert
            cache_ttl: Cache-TTL in Sekunden
        """
        try:
            # Konfiguration
            self.index_path = Path(index_path)
            self.batch_size = batch_size
            self.gpu_memory_threshold = gpu_memory_threshold
            self.cache_ttl = cache_ttl

            # Verzeichnis erstellen
            self.index_path.mkdir(parents=True, exist_ok=True)

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

            # Indizes laden oder erstellen
            self.indices: Dict[str, Any] = {}
            self._load_indices()

            logger.info(
                "Vector DB initialisiert",
                extra={
                    "index_path": str(self.index_path),
                    "batch_size": batch_size,
                    "device": str(self.device),
                    "faiss_available": _FAISS_AVAILABLE,
                },
            )

        except Exception:
            logger.error("Error creating embeddings")
            raise

    def _load_indices(self) -> None:
        """Lädt existierende Indizes oder erstellt neue."""
        try:
            if not _FAISS_AVAILABLE:
                logger.warning("FAISS nicht verfügbar - Mock-Modus aktiv")
                return

            for index_file in self.index_path.glob("*.index"):
                collection_name = index_file.stem
                # Type-ignore für FAISS-API die zur Laufzeit verfügbar ist
                self.indices[collection_name] = faiss.read_index(str(index_file))  # type: ignore

            logger.info(f"Geladene Indizes: {list(self.indices.keys())}")

        except Exception:
            logger.error("Error loading indices")
            raise

    def _adjust_batch_size(self) -> None:
        """Passt die Batch-Größe basierend auf GPU-Speicher an."""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated()
            memory_reserved = torch.cuda.memory_reserved()

            try:
                device_props = torch.cuda.get_device_properties(0)
                total_memory = float(device_props.total_memory)  # type: ignore
                memory_usage = float(memory_allocated + memory_reserved) / total_memory

                if memory_usage > self.gpu_memory_threshold:
                    self.batch_size = max(100, self.batch_size // 2)
                    logger.warning(
                        "Batch-Größe reduziert",
                        extra={
                            "new_batch_size": self.batch_size,
                            "memory_usage": float(memory_usage),
                        },
                    )
                elif memory_usage < self.gpu_memory_threshold * 0.5:
                    self.batch_size = min(10000, self.batch_size * 2)
                    logger.info(
                        "Batch-Größe erhöht",
                        extra={
                            "new_batch_size": self.batch_size,
                            "memory_usage": float(memory_usage),
                        },
                    )
            except Exception as e:
                logger.warning(f"GPU-Memory-Check fehlgeschlagen: {e}")

    def _cleanup_gpu_memory(self) -> None:
        """Bereinigt GPU-Speicher."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        """
        Gibt Informationen über eine Collection zurück.

        Args:
            collection_name: Name der Collection

        Returns:
            CollectionInfo mit Metadaten der Collection
        """
        if collection_name not in self.indices:
            raise ValueError(f"Collection {collection_name} existiert nicht")

        index = self.indices[collection_name]

        if _FAISS_AVAILABLE and hasattr(index, 'ntotal'):
            vector_count = index.ntotal
            vector_size = index.d if hasattr(index, 'd') else 0
        else:
            vector_count = 0
            vector_size = 0

        return CollectionInfo(
            name=collection_name,
            vector_count=vector_count,
            vector_size=vector_size,
            status="ready" if _FAISS_AVAILABLE else "mock",
            indexed=True
        )

    async def upsert_vector(
        self,
        collection_name: str,
        vector: List[float],
        vector_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Fügt einen einzelnen Vektor zur Collection hinzu oder aktualisiert ihn.

        Args:
            collection_name: Name der Collection
            vector: Vektor-Daten
            vector_id: Eindeutige ID des Vektors
            metadata: Optionale Metadaten

        Returns:
            True wenn erfolgreich
        """
        try:
            vector_array = np.array([vector], dtype=np.float32)
            return await self.upsert_vectors(
                collection_name=collection_name,
                vectors=[vector_array[0]],
                ids=[hash(vector_id)]  # String-ID zu Int-Hash konvertieren
            )
        except Exception:
            logger.error("Error upserting single vector")
            return False

    async def create_collection(self, collection_name: str, dimension: int) -> bool:
        """
        Erstellt eine neue Collection.

        Args:
            collection_name: Name der Collection
            dimension: Dimension der Vektoren

        Returns:
            True wenn erfolgreich
        """
        try:
            if collection_name in self.indices:
                logger.warning(f"Collection {collection_name} existiert bereits")
                return False

            # GPU-Index erstellen
            if torch.cuda.is_available():
                config = faiss.GpuIndexFlatConfig()
                config.device = 0
                index = faiss.GpuIndexFlatL2(
                    faiss.StandardGpuResources(), dimension, config
                )
            else:
                index = faiss.IndexFlatL2(dimension)

            self.indices[collection_name] = index

            # Index speichern
            index_path = self.index_path / f"{collection_name}.index"
            faiss.write_index(index, str(index_path))

            logger.info(
                f"Collection {collection_name} erstellt", extra={"dimension": dimension}
            )

            return True

        except Exception:
            logger.error("Error creating collection")
            raise

    async def upsert_vectors(
        self,
        collection_name: str,
        vectors: List[np.ndarray[Any, Any]],
        ids: Optional[List[int]] = None,
    ) -> bool:
        """
        Fügt Vektoren zur Collection hinzu oder aktualisiert sie.

        Args:
            collection_name: Name der Collection
            vectors: Liste von Vektoren
            ids: Optionale IDs für die Vektoren

        Returns:
            True wenn erfolgreich
        """
        try:
            if collection_name not in self.indices:
                raise ValueError(f"Collection {collection_name} existiert nicht")

            # Batch-Verarbeitung
            for i in range(0, len(vectors), self.batch_size):
                batch_vectors = vectors[i : i + self.batch_size]
                batch_ids = ids[i : i + self.batch_size] if ids else None

                # Vektoren in GPU-Speicher laden
                if torch.cuda.is_available():
                    batch_vectors = torch.tensor(batch_vectors, device=self.device)

                # Vektoren hinzufügen
                if batch_ids:
                    self.indices[collection_name].add_with_ids(batch_vectors, batch_ids)
                else:
                    self.indices[collection_name].add(batch_vectors)

                # Batch-Größe anpassen
                self._adjust_batch_size()

                # GPU-Speicher bereinigen
                self._cleanup_gpu_memory()

            # Index speichern
            index_path = self.index_path / f"{collection_name}.index"
            faiss.write_index(self.indices[collection_name], str(index_path))

            logger.info(
                f"Vektoren zu {collection_name} hinzugefügt",
                extra={"vector_count": len(vectors)},
            )

            return True

        except Exception:
            logger.error("Error upserting vectors")
            raise

    async def search_vectors(
        self, collection_name: str, query_vectors: List[np.ndarray], k: int = 10
    ) -> List[Tuple[List[int], List[float]]]:
        """
        Sucht nach ähnlichen Vektoren.

        Args:
            collection_name: Name der Collection
            query_vectors: Suchvektoren
            k: Anzahl der Ergebnisse

        Returns:
            Liste von (IDs, Distanzen)-Tupeln
        """
        try:
            if collection_name not in self.indices:
                raise ValueError(f"Collection {collection_name} existiert nicht")

            results = []

            # Batch-Verarbeitung
            for i in range(0, len(query_vectors), self.batch_size):
                batch_vectors = query_vectors[i : i + self.batch_size]

                # Cache-Key generieren
                cache_key = (
                    f"search:{collection_name}:{hash(batch_vectors.tobytes())}:{k}"
                )

                # Cache prüfen
                cached_result = self.redis_client.get(cache_key)
                if cached_result:
                    results.extend(pickle.loads(cached_result))
                    continue

                # Vektoren in GPU-Speicher laden
                if torch.cuda.is_available():
                    batch_vectors = torch.tensor(batch_vectors, device=self.device)

                # Suche durchführen
                distances, indices = self.indices[collection_name].search(
                    batch_vectors, k
                )

                # Ergebnisse cachen
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    pickle.dumps(list(zip(indices, distances))),
                )

                results.extend(zip(indices, distances))

                # Batch-Größe anpassen
                self._adjust_batch_size()

                # GPU-Speicher bereinigen
                self._cleanup_gpu_memory()

            return results

        except Exception:
            logger.error("Error searching vectors")
            raise

    async def delete_collection(self, collection_name: str) -> bool:
        """
        Löscht eine Collection.

        Args:
            collection_name: Name der Collection

        Returns:
            True wenn erfolgreich
        """
        try:
            if collection_name not in self.indices:
                logger.warning(f"Collection {collection_name} existiert nicht")
                return False

            # Index löschen
            del self.indices[collection_name]

            # Datei löschen
            index_path = self.index_path / f"{collection_name}.index"
            if index_path.exists():
                index_path.unlink()

            # Cache löschen
            pattern = f"search:{collection_name}:*"
            for key in self.redis_client.scan_iter(pattern):
                self.redis_client.delete(key)

            logger.info(f"Collection {collection_name} gelöscht")

            return True

        except Exception:
            logger.error("Error deleting collection")
            raise


# Service-Instanz erstellen
vector_db_service = VectorDB()


@app.post("/collections")
async def create_collection(config: CollectionConfig):
    """
    Erstellt eine neue Collection
    """
    try:
        success = await vector_db_service.create_collection(
            config.name, config.vector_size
        )
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
        success = await vector_db_service.upsert_vector(
            vector.collection, vector.vector, vector.id, vector.metadata
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vectors/batch")
async def upsert_vectors_batch(batch: BatchVector):
    """
    Speichert oder aktualisiert mehrere Vektoren in einem Batch
    """
    try:
        success = await vector_db_service.upsert_vectors(
            batch.collection, batch.vectors, batch.batch_size
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search")
async def search_vectors(request: SearchRequest):
    """
    Sucht ähnliche Vektoren
    """
    try:
        results = await vector_db_service.search_vectors(
            request.collection, request.vector, request.limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/vectors/{collection}/{vector_id}")
async def delete_vector(collection: str, vector_id: str):
    """
    Löscht einen Vektor
    """
    try:
        success = await vector_db_service.delete_collection(collection)
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
            "redis": "available" if redis_healthy else "unavailable",
        }
    except Exception:
        logger.error("Error in health check")
        return {"status": "unhealthy", "error": "Health check failed"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

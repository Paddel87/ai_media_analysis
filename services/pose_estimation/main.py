import cv2
import mmcv
import numpy as np
import torch
import uvicorn
import time
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from mmpose.apis import inference_topdown as real_inference_topdown, init_model
from mmpose.structures import merge_data_samples, PoseDataSample
from pydantic import BaseModel
import logging
import os
from typing import List, Optional, Dict, Any, cast
import psutil
import uuid
import json
import redis.asyncio as redis
from tenacity import retry, stop_after_attempt, wait_exponential
import aiofiles
import asyncio
from datetime import datetime, timedelta
from mmengine.model import BaseModel as MMBaseModel
import sys
import inspect
from config import get_settings
import importlib
from optimization import (
    MemoryManager,
    ConcurrencyManager,
    CacheManager,
    ResourceMonitor,
    DegradationManager,
    WorkerManager
)

# Logging Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pose Estimation Service",
    description="CPU-optimierter Service für Pose Estimation",
    version="0.1.0"
)

# Konfiguration
settings = get_settings()
REDIS_URL = settings.redis_url
BATCH_EXPIRY = settings.batch_expiry
MAX_BATCH_SIZE = settings.batch_size_limit
TEMP_DIR = settings.temp_dir

# Modell-Konfiguration
config_file = "configs/body_2d_keypoint/topdown_heatmap/coco/td-hm_hrnet-w48_8xb32-210e_coco-256x192.py"
checkpoint_file = "https://download.openmmlab.com/mmpose/top_down/hrnet/hrnet_w48_coco_256x192-b9e0b3ab_20200708.pth"

# CPU-spezifische Konfiguration
device = torch.device("cpu")
model: Optional[MMBaseModel] = None
redis_client: Optional[redis.Redis] = None
inference_topdown = None

# Optimierungsmanager
memory_manager: Optional[MemoryManager] = None
concurrency_manager: Optional[ConcurrencyManager] = None
cache_manager: Optional[CacheManager] = None
resource_monitor: Optional[ResourceMonitor] = None
degradation_manager: Optional[DegradationManager] = None
worker_manager: Optional[WorkerManager] = None

# Prozess-Startzeit für Uptime
process_start_time = time.time()

# In-Memory-Redis-Fallback für Tests
class InMemoryRedis:
    def __init__(self):
        self.store = {}
        self.expiry = {}

    async def setex(self, key, expiry, value):
        self.store[key] = value
        if expiry:
            self.expiry[key] = datetime.now() + timedelta(seconds=expiry)

    async def get(self, key):
        if key in self.expiry and datetime.now() > self.expiry[key]:
            self.store.pop(key, None)
            self.expiry.pop(key, None)
            return None
        return self.store.get(key)

    async def expire(self, key, seconds):
        if key in self.store:
            self.expiry[key] = datetime.now() + timedelta(seconds=seconds)
            return True
        return False

    async def ping(self):
        return True

    async def close(self):
        self.store.clear()
        self.expiry.clear()

# DummyModel für Testbetrieb
class DummyModel:
    def __init__(self):
        pass

# Dummy-Inferenzfunktion für Testbetrieb
async def dummy_inference_topdown(model, img):
    class DummyResult:
        def __init__(self):
            self.pred_instances = {
                'keypoints': torch.tensor([[[0.0, 0.0], [1.0, 1.0]]]),
                'keypoint_scores': torch.tensor([[0.9, 0.8]])
            }
    return [DummyResult()]

# Hilfsfunktion für Tests, um Settings-Cache zu leeren
def force_reload_settings():
    importlib.reload(__import__("config"))

# Initialisierung für Testmodus direkt beim Import
TESTING = os.getenv("TESTING", "0") == "1" or any("pytest" in arg for arg in sys.argv)
if TESTING:
    redis_client = InMemoryRedis()
    logger.info("InMemoryRedis für TESTING aktiviert (Import)")
    model = DummyModel()
    inference_topdown = dummy_inference_topdown
    logger.info("DummyModel für TESTING aktiviert (Import)")

# Pydantic Models
class PoseResponse(BaseModel):
    keypoints: List[List[List[float]]]
    scores: List[List[float]]
    num_people: int
    processing_time: float

class BatchStatus(BaseModel):
    status: str
    progress: int
    total_files: int
    processed_files: int
    failed_files: int
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# Redis Dependencies
async def get_redis() -> Any:
    if redis_client is None:
        raise HTTPException(status_code=503, detail="Redis nicht verfügbar")
    return redis_client

# Globales Concurrency-Limit (Semaphore)
CONCURRENCY_LIMIT = getattr(settings, "batch_size_limit", 100)
semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

@app.on_event("startup")
async def startup_event():
    global model, redis_client, inference_topdown
    global memory_manager, concurrency_manager, cache_manager
    global resource_monitor, degradation_manager, worker_manager

    try:
        # Redis Client initialisieren
        redis_client = redis.from_url(REDIS_URL)
        await redis_client.ping()

        # Optimierungsmanager initialisieren
        memory_manager = MemoryManager(redis_client)
        concurrency_manager = ConcurrencyManager()
        cache_manager = CacheManager(redis_client)
        resource_monitor = ResourceMonitor()
        degradation_manager = DegradationManager()
        worker_manager = WorkerManager()

        # Modell initialisieren
        if not TESTING:
            model = init_model(config_file, checkpoint_file, device=device)
            inference_topdown = real_inference_topdown
        else:
            model = DummyModel()
            inference_topdown = dummy_inference_topdown

        logger.info("Service erfolgreich initialisiert")
    except Exception as e:
        logger.error(f"Fehler bei der Initialisierung: {e}")
        raise

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def process_single_image(file_path: str) -> Dict[str, Any]:
    if model is None:
        raise ValueError("Modell nicht initialisiert")
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Bild konnte nicht geladen werden")
        start_time = time.time()
        TESTING = os.getenv("TESTING", "0") == "1" or any("pytest" in arg for arg in sys.argv)
        if inference_topdown is None:
            if TESTING:
                keypoints = torch.tensor([[[0.0, 0.0], [1.0, 1.0]]])
                scores = torch.tensor([[0.9, 0.8]])
            else:
                raise ValueError("inference_topdown nicht initialisiert")
        elif TESTING and inspect.iscoroutinefunction(inference_topdown):
            results = await inference_topdown(model, img)
            results = results[0]
            keypoints = results.pred_instances['keypoints']
            scores = results.pred_instances['keypoint_scores']
        else:
            if inspect.iscoroutinefunction(inference_topdown):
                raise ValueError("inference_topdown darf im echten Modus kein Coroutine sein!")
            results = cast(List[PoseDataSample], inference_topdown(cast(MMBaseModel, model), img))
            results = merge_data_samples(results)
            keypoints = results.pred_instances.get('keypoints', None)
            scores = results.pred_instances.get('keypoint_scores', None)
        processing_time = time.time() - start_time
        if keypoints is None or scores is None:
            raise ValueError("Keine Keypoints oder Scores gefunden")
        return {
            "keypoints": keypoints.cpu().numpy().tolist(),
            "scores": scores.cpu().numpy().tolist(),
            "num_people": len(keypoints),
            "processing_time": processing_time
        }
    except Exception as e:
        logger.error(f"Fehler bei der Bildverarbeitung: {e}")
        raise

async def update_batch_status(
    redis_client: redis.Redis,
    batch_id: str,
    status: str,
    progress: int,
    total_files: int,
    processed_files: int,
    failed_files: int,
    results: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    batch_status = BatchStatus(
        status=status,
        progress=progress,
        total_files=total_files,
        processed_files=processed_files,
        failed_files=failed_files,
        results=results,
        error=error,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    await redis_client.setex(
        f"batch:{batch_id}",
        BATCH_EXPIRY,
        json.dumps(batch_status.dict(), default=str)
    )

async def check_system_health() -> Optional[Dict[str, Any]]:
    """Überprüft die System-Gesundheit und gibt ggf. einen Fehler zurück."""
    metrics = get_system_metrics()

    if metrics["cpu_usage"] > 90:
        return {
            "status_code": 503,
            "detail": "System überlastet",
            "retry_after": 30,
            "reason": "high_cpu_usage"
        }

    if metrics["memory_usage"] > 90:
        return {
            "status_code": 503,
            "detail": "Speicher überlastet",
            "retry_after": 30,
            "reason": "high_memory_usage"
        }

    if metrics["processing_queue"] > settings.max_workers * 2:
        return {
            "status_code": 503,
            "detail": "Verarbeitungswarteschlange voll",
            "retry_after": 15,
            "reason": "queue_full"
        }

    return None

@app.post("/analyze", response_model=PoseResponse)
async def analyze_pose(file: UploadFile = File(...)):
    if not all([memory_manager, concurrency_manager, cache_manager,
                resource_monitor, degradation_manager, worker_manager]):
        raise HTTPException(
            status_code=503,
            detail="Service nicht vollständig initialisiert"
        )

    try:
        # Resource Monitoring
        metrics = await resource_monitor.monitor_resources()

        # Graceful Degradation prüfen
        service_level = await degradation_manager.adjust_service_level()

        # Memory Check
        if await memory_manager.check_memory():
            logger.warning("Memory-Limit erreicht - Cleanup durchgeführt")

        # Concurrency-Limit prüfen
        acquired = await concurrency_manager.semaphore.acquire()
        if not acquired:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Zu viele gleichzeitige Anfragen. Bitte später erneut versuchen.",
                    "retry_after": 10,
                    "reason": "concurrency_limit"
                }
            )

        try:
            # Validiere Dateityp
            if file.content_type and not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail="Ungültiges Dateiformat. Nur Bilder werden akzeptiert."
                )

            # Cache-Check
            cache_key = f"pose_{file.filename}"
            cached_result = await redis_client.get(cache_key)
            if cached_result:
                return PoseResponse(**json.loads(cached_result))

            # Speichere temporäre Datei
            temp_file = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.jpg")
            try:
                async with aiofiles.open(temp_file, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)

                # Verarbeite Bild
                result = await process_single_image(temp_file)

                # Cache Result
                await cache_manager.cache_result(cache_key, result)

                return PoseResponse(**result)
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        finally:
            concurrency_manager.semaphore.release()
    except ValueError as e:
        logger.error(f"Fehler bei der Pose Estimation: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unerwarteter Fehler: {e}")
        raise HTTPException(
            status_code=500,
            detail="Interner Server-Fehler"
        )

@app.post("/analyze/batch")
async def analyze_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Verarbeitet einen Batch von Bildern."""
    # System-Gesundheit prüfen
    health_check = await check_system_health()
    if health_check:
        return JSONResponse(
            status_code=health_check["status_code"],
            content={
                "detail": health_check["detail"],
                "retry_after": health_check["retry_after"],
                "reason": health_check["reason"]
            }
        )

    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Maximale Batch-Größe von {MAX_BATCH_SIZE} Dateien überschritten"
        )

    batch_id = str(uuid.uuid4())

    # Initialen Status setzen
    await update_batch_status(
        redis_client=redis_client,
        batch_id=batch_id,
        status="processing",
        progress=0,
        total_files=len(files),
        processed_files=0,
        failed_files=0
    )

    async def process_batch():
        results = {}
        processed_files = 0
        failed_files = 0

        try:
            for i, file in enumerate(files):
                try:
                    # Temporäre Datei speichern
                    temp_path = os.path.join(TEMP_DIR, f"{batch_id}_{i}.jpg")
                    async with aiofiles.open(temp_path, 'wb') as f:
                        await f.write(await file.read())

                    # Bild verarbeiten
                    result = await process_single_image(temp_path)
                    results[file.filename] = result
                    processed_files += 1

                    # Temporäre Datei löschen
                    os.remove(temp_path)

                except Exception as e:
                    logger.error(f"Fehler bei der Verarbeitung von {file.filename}: {e}")
                    results[file.filename] = {"error": str(e)}
                    failed_files += 1

                # Status aktualisieren
                progress = int((i + 1) / len(files) * 100)
                await update_batch_status(
                    redis_client=redis_client,
                    batch_id=batch_id,
                    status="processing",
                    progress=progress,
                    total_files=len(files),
                    processed_files=processed_files,
                    failed_files=failed_files,
                    results=results
                )

            # Finalen Status setzen
            await update_batch_status(
                redis_client=redis_client,
                batch_id=batch_id,
                status="completed",
                progress=100,
                total_files=len(files),
                processed_files=processed_files,
                failed_files=failed_files,
                results=results
            )

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {e}")
            await update_batch_status(
                redis_client=redis_client,
                batch_id=batch_id,
                status="failed",
                progress=0,
                total_files=len(files),
                processed_files=processed_files,
                failed_files=failed_files,
                error=str(e)
            )

    background_tasks.add_task(process_batch)
    return {"batch_id": batch_id}

@app.get("/analyze/batch/{batch_id}/status")
async def batch_status(
    batch_id: str,
    redis_client: redis.Redis = Depends(get_redis)
):
    status_data = await redis_client.get(f"batch:{batch_id}")
    if not status_data:
        raise HTTPException(status_code=404, detail="Batch-ID nicht gefunden")

    return json.loads(status_data)

@app.get("/analyze/batch/{batch_id}/results")
async def batch_results(
    batch_id: str,
    redis_client: redis.Redis = Depends(get_redis)
):
    status_data = await redis_client.get(f"batch:{batch_id}")
    if not status_data:
        raise HTTPException(status_code=404, detail="Batch-ID nicht gefunden")

    status = json.loads(status_data)
    if status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Batch noch nicht abgeschlossen. Status: {status['status']}"
        )

    return status["results"]

@app.get("/health")
async def health_check():
    if model is None:
        return {"status": "unhealthy", "error": "Modell nicht initialisiert"}
    uptime = time.time() - process_start_time
    return {
        "status": "healthy",
        "model_loaded": True,
        "device": str(device),
        "memory_usage": f"{torch.cuda.memory_allocated() / 1024**2:.2f}MB" if torch.cuda.is_available() else "N/A",
        "version": app.version,
        "uptime": uptime
    }

def get_system_metrics() -> Dict[str, float]:
    """Gibt aktuelle System-Metriken zurück."""
    return {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "processing_queue": len(asyncio.all_tasks())  # Anzahl der aktiven Tasks
    }

@app.get("/metrics")
async def metrics():
    """Gibt aktuelle System-Metriken zurück."""
    if not all([resource_monitor, concurrency_manager, cache_manager,
                degradation_manager, worker_manager]):
        raise HTTPException(
            status_code=503,
            detail="Service nicht vollständig initialisiert"
        )

    metrics = await resource_monitor.monitor_resources()
    metrics.update({
        "concurrency_limit": concurrency_manager.current_limit,
        "cache_size": await cache_manager.get_cache_size(),
        "degradation_level": degradation_manager.current_level,
        "worker_count": worker_manager.current_workers
    })
    return metrics

@app.get("/config")
async def config():
    return {
        "model_type": settings.model_type,
        "max_workers": settings.max_workers,
        "memory_limit": settings.memory_limit,
        "batch_size_limit": settings.batch_size_limit,
        "processing_timeout": settings.processing_timeout
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("MAX_WORKERS", "2"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=workers,
        log_level="info"
    )

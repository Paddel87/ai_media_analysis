"""
Job Manager - Task Orchestration Service
Zentrale Task-Orchestrierung für das AI Media Analysis System
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# FastAPI App
app = FastAPI(
    title="Job Manager",
    description="Task Orchestration Service für AI Media Analysis",
    version="1.0.0"
)

# Environment Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 1))
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", 10))
JOB_TIMEOUT = int(os.getenv("JOB_TIMEOUT", 3600))
BATCH_ID = os.getenv("BATCH_ID", "default_batch")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Global Variables
redis_client = None
active_jobs = {}

# Logging
logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper()))
logger = logging.getLogger("job_manager")

class JobRequest(BaseModel):
    job_type: str
    input_data: Dict[str, Any]
    priority: int = 1
    timeout: Optional[int] = None

class JobResponse(BaseModel):
    job_id: str
    status: str
    created_at: str
    estimated_duration: Optional[int] = None

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str

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
            socket_timeout=5
        )
        # Test connection
        redis_client.ping()
        logger.info(f"Redis verbunden: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return True
    except Exception as e:
        logger.error(f"Redis Verbindungsfehler: {e}")
        redis_client = None
        return False

async def process_job_queue():
    """Background Task für Job-Queue-Processing"""
    while True:
        try:
            if redis_client and len(active_jobs) < MAX_CONCURRENT_JOBS:
                # Job aus Queue holen
                job_data = redis_client.brpop("job_queue", timeout=1)
                if job_data:
                    job_info = json.loads(job_data[1])
                    job_id = job_info["job_id"]

                    # Job als aktiv markieren
                    active_jobs[job_id] = {
                        "started_at": datetime.now().isoformat(),
                        "status": "processing"
                    }

                    # Job-Status in Redis aktualisieren
                    redis_client.hset(f"job:{job_id}", mapping={
                        "status": "processing",
                        "updated_at": datetime.now().isoformat()
                    })

                    logger.info(f"Job {job_id} gestartet")

                    # TODO: Hier würde die tatsächliche Job-Verarbeitung stattfinden
                    # Für jetzt: Dummy-Processing
                    await asyncio.sleep(2)  # Simuliere Arbeit

                    # Job als abgeschlossen markieren
                    active_jobs.pop(job_id, None)
                    redis_client.hset(f"job:{job_id}", mapping={
                        "status": "completed",
                        "progress": 100,
                        "updated_at": datetime.now().isoformat(),
                        "result": json.dumps({"processed": True, "batch_id": BATCH_ID})
                    })

                    logger.info(f"Job {job_id} abgeschlossen")

            await asyncio.sleep(0.1)  # Kurze Pause

        except Exception as e:
            logger.error(f"Job-Queue-Fehler: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    """Startup Event Handler"""
    logger.info("Job Manager startet...")

    # Redis initialisieren
    await init_redis()

    # Service-Status in Redis setzen
    if redis_client:
        service_info = {
            "service": "job_manager",
            "status": "running",
            "batch_id": BATCH_ID,
            "max_concurrent_jobs": MAX_CONCURRENT_JOBS,
            "started_at": datetime.now().isoformat()
        }
        redis_client.hset("system:job_manager", mapping=service_info)

    # Background Job-Processing starten
    asyncio.create_task(process_job_queue())

    logger.info("Job Manager bereit")

@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    redis_status = False
    if redis_client:
        try:
            redis_client.ping()
            redis_status = True
        except:
            redis_status = False

    return {
        "status": "healthy" if redis_status else "degraded",
        "service": "job_manager",
        "redis_connected": redis_status,
        "active_jobs": len(active_jobs),
        "max_concurrent_jobs": MAX_CONCURRENT_JOBS,
        "batch_id": BATCH_ID,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/jobs", response_model=JobResponse)
async def create_job(job_request: JobRequest):
    """Neuen Job erstellen"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis nicht verfügbar")

        job_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        # Job-Daten
        job_data = {
            "job_id": job_id,
            "job_type": job_request.job_type,
            "input_data": job_request.input_data,
            "priority": job_request.priority,
            "timeout": job_request.timeout or JOB_TIMEOUT,
            "status": "queued",
            "progress": 0,
            "created_at": created_at,
            "updated_at": created_at,
            "batch_id": BATCH_ID
        }

        # Job in Redis speichern
        redis_client.hset(f"job:{job_id}", mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in job_data.items()
        })

        # Job in Queue einreihen
        redis_client.lpush("job_queue", json.dumps(job_data))

        logger.info(f"Job {job_id} erstellt: {job_request.job_type}")

        return JobResponse(
            job_id=job_id,
            status="queued",
            created_at=created_at,
            estimated_duration=job_request.timeout
        )

    except Exception as e:
        logger.error(f"Job-Erstellungs-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Job-Status abrufen"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis nicht verfügbar")

        job_data = redis_client.hgetall(f"job:{job_id}")
        if not job_data:
            raise HTTPException(status_code=404, detail="Job nicht gefunden")

        # JSON-Felder parsen
        result = None
        if job_data.get("result"):
            try:
                result = json.loads(job_data["result"])
            except:
                result = {"raw": job_data["result"]}

        return JobStatus(
            job_id=job_id,
            status=job_data["status"],
            progress=float(job_data.get("progress", 0)),
            result=result,
            error=job_data.get("error"),
            created_at=job_data["created_at"],
            updated_at=job_data["updated_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Job-Status-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def list_jobs(status: Optional[str] = None, limit: int = 100):
    """Jobs auflisten"""
    try:
        if not redis_client:
            raise HTTPException(status_code=503, detail="Redis nicht verfügbar")

        # Alle Job-Keys finden
        job_keys = redis_client.keys("job:*")
        jobs = []

        for key in job_keys[:limit]:
            job_data = redis_client.hgetall(key)
            if status and job_data.get("status") != status:
                continue

            jobs.append({
                "job_id": key.split(":")[1],
                "job_type": job_data.get("job_type", "unknown"),
                "status": job_data.get("status", "unknown"),
                "progress": float(job_data.get("progress", 0)),
                "created_at": job_data.get("created_at"),
                "updated_at": job_data.get("updated_at")
            })

        return {
            "jobs": jobs,
            "count": len(jobs),
            "total_keys": len(job_keys)
        }

    except Exception as e:
        logger.error(f"Job-Listen-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Service-Statistiken"""
    try:
        queue_length = 0
        if redis_client:
            queue_length = redis_client.llen("job_queue")

        return {
            "service": "job_manager",
            "batch_id": BATCH_ID,
            "active_jobs": len(active_jobs),
            "max_concurrent_jobs": MAX_CONCURRENT_JOBS,
            "queue_length": queue_length,
            "redis_connected": redis_client is not None,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Stats-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level=LOG_LEVEL.lower()
    )

import asyncio
import json
import logging
import os
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from manager import JobManager
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Job Manager API")
job_manager = JobManager()


class BatchCreateRequest(BaseModel):
    job_ids: List[str]
    batch_name: Optional[str] = None


class BatchResponse(BaseModel):
    batch_id: str
    status: str
    jobs: List[dict]
    created_at: str
    estimated_duration: float
    created_by: str


@app.on_event("startup")
async def startup_event():
    """Startet den Job-Manager im Hintergrund"""
    asyncio.create_task(job_manager.start())


@app.post("/batches", response_model=BatchResponse)
async def create_batch(request: BatchCreateRequest):
    """Erstellt einen neuen Batch manuell"""
    try:
        batch_id = await job_manager.create_batch(
            job_ids=request.job_ids, batch_name=request.batch_name
        )

        # Batch-Metadaten laden
        batch_path = f"data/jobs/{batch_id}"
        with open(f"{batch_path}/metadata.json", "r") as f:
            batch_data = json.load(f)

        return BatchResponse(**batch_data)

    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Batches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batches/{batch_id}/start")
async def start_batch_processing(batch_id: str):
    """Startet die Verarbeitung eines Batches"""
    try:
        await job_manager.start_batch_processing(batch_id)
        return {"message": f"Batch {batch_id} Verarbeitung gestartet"}

    except Exception as e:
        logger.error(f"Fehler beim Starten der Batch-Verarbeitung: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch(batch_id: str):
    """Gibt die Metadaten eines Batches zurück"""
    try:
        batch_path = f"data/jobs/{batch_id}"
        metadata_path = f"{batch_path}/metadata.json"

        if not os.path.exists(metadata_path):
            raise HTTPException(
                status_code=404, detail=f"Batch {batch_id} nicht gefunden"
            )

        with open(metadata_path, "r") as f:
            batch_data = json.load(f)

        return BatchResponse(**batch_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Batches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/batches", response_model=List[BatchResponse])
async def list_batches():
    """Listet alle Batches"""
    try:
        batches = []
        batch_path = "data/jobs"

        if not os.path.exists(batch_path):
            return []

        for batch_id in os.listdir(batch_path):
            metadata_path = f"{batch_path}/{batch_id}/metadata.json"
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    batch_data = json.load(f)
                    batches.append(BatchResponse(**batch_data))

        return batches

    except Exception as e:
        logger.error(f"Fehler beim Auflisten der Batches: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/pending")
async def list_pending_jobs():
    """Listet alle wartenden Jobs"""
    try:
        jobs = job_manager.get_pending_jobs()
        return {"jobs": jobs}

    except Exception as e:
        logger.error(f"Fehler beim Auflisten der wartenden Jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/settings/auto-process")
async def set_auto_process(enabled: bool):
    """Aktiviert oder deaktiviert die automatische Job-Verarbeitung"""
    try:
        job_manager.auto_process_jobs = enabled
        return {
            "message": f"Automatische Verarbeitung {'aktiviert' if enabled else 'deaktiviert'}"
        }

    except Exception as e:
        logger.error(f"Fehler beim Ändern der Auto-Process-Einstellung: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/settings/auto-process")
async def get_auto_process():
    """Gibt den aktuellen Status der automatischen Job-Verarbeitung zurück"""
    return {"enabled": job_manager.auto_process_jobs}

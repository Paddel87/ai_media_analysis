import os
from datetime import datetime
from typing import List, Optional

import aiohttp
import redis
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from main import VisionPipeline
from pydantic import BaseModel, Field, validator
from rq import Queue
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("vision_pipeline_api")

# Rate Limiter konfigurieren
limiter = Limiter(key_func=get_remote_address)

# FastAPI-App erstellen
app = FastAPI(
    title="Vision Pipeline API",
    version="1.0.0",
    description="""
API für die Verarbeitung von Bildern und Videos mit KI-Modulen.

## Features
- Parallele Verarbeitung mehrerer Videos und Bilder
- Optimiertes Batch-Processing für effiziente GPU-Nutzung
- Asynchrone Verarbeitung mit Job-Queue
- Frame-Sampling für effiziente Video-Analyse

## Fehlercodes
- 400: Ungültige Anfrage (z.B. nicht unterstütztes Dateiformat)
- 404: Job nicht gefunden
- 429: Zu viele Anfragen
- 503: Service nicht verfügbar
- 500: Interner Serverfehler
""",
)

# CORS konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion auf spezifische Domains beschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiter Exception Handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Redis-Verbindung konfigurieren
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
redis_conn = redis.Redis(host=redis_host, port=redis_port)

# Job-Queue erstellen
queue = Queue("vision_pipeline", connection=redis_conn)

# Job-Manager-URL
job_manager_url = os.getenv("JOB_MANAGER_URL", "http://job_manager_api:8000")

# Pipeline-Instanz erstellen
pipeline = VisionPipeline(
    output_dir=os.getenv("OUTPUT_DIR", "data/output"),
    pose_service_url=os.getenv("POSE_SERVICE_URL"),
    ocr_service_url=os.getenv("OCR_SERVICE_URL"),
    nsfw_service_url=os.getenv("NSFW_SERVICE_URL"),
    batch_size=int(os.getenv("BATCH_SIZE", 4)),
    frame_sampling_rate=int(os.getenv("FRAME_SAMPLING_RATE", 2)),
    max_workers=int(os.getenv("MAX_WORKERS", 4)),
)


# Pydantic-Modelle
class VideoAnalysisRequest(BaseModel):
    video_paths: List[str] = Field(
        ...,
        description="Liste der Video-Pfade",
        example=["/data/videos/video1.mp4", "/data/videos/video2.mp4"],
    )
    batch_size: Optional[int] = Field(
        4, description="Anzahl der Frames pro Batch", ge=1, le=32
    )
    frame_sampling_rate: Optional[int] = Field(
        2, description="Jedes n-te Frame wird analysiert", ge=1, le=10
    )
    priority: Optional[int] = Field(1, description="Job-Priorität (1-5)", ge=1, le=5)

    @validator("video_paths")
    def validate_video_paths(cls, paths):
        for path in paths:
            if not os.path.exists(path):
                raise ValueError(f"Video nicht gefunden: {path}")
            if not path.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                raise ValueError(f"Nicht unterstütztes Video-Format: {path}")
        return paths

    @validator("priority")
    def validate_priority(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Priorität muss zwischen 1 und 5 liegen")
        return v


class ImageAnalysisRequest(BaseModel):
    image_paths: List[str] = Field(
        ...,
        description="Liste der Bild-Pfade",
        example=["/data/images/image1.jpg", "/data/images/image2.jpg"],
    )
    batch_size: Optional[int] = Field(
        4, description="Anzahl der Bilder pro Batch", ge=1, le=32
    )
    priority: Optional[int] = Field(1, description="Job-Priorität (1-5)", ge=1, le=5)

    @validator("image_paths")
    def validate_image_paths(cls, paths):
        for path in paths:
            if not os.path.exists(path):
                raise ValueError(f"Bild nicht gefunden: {path}")
            if not path.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                raise ValueError(f"Nicht unterstütztes Bild-Format: {path}")
        return paths

    @validator("priority")
    def validate_priority(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Priorität muss zwischen 1 und 5 liegen")
        return v


class JobResponse(BaseModel):
    job_id: str = Field(..., description="Eindeutige Job-ID")
    status: str = Field(..., description="Aktueller Job-Status")
    created_at: str = Field(..., description="Erstellungszeitpunkt")
    priority: int = Field(..., description="Job-Priorität")


class JobStatus(BaseModel):
    job_id: str = Field(..., description="Eindeutige Job-ID")
    status: str = Field(..., description="Aktueller Job-Status")
    created_at: str = Field(..., description="Erstellungszeitpunkt")
    updated_at: Optional[str] = Field(None, description="Letzte Aktualisierung")
    result: Optional[dict] = Field(None, description="Analyseergebnisse")
    error: Optional[str] = Field(None, description="Fehlermeldung")
    priority: int = Field(..., description="Job-Priorität")


async def register_job_with_manager(job_id: str, job_type: str, priority: int):
    """Registriert einen Job beim Job-Manager."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{job_manager_url}/jobs/register",
                json={
                    "job_id": job_id,
                    "job_type": job_type,
                    "priority": priority,
                    "service": "vision_pipeline",
                },
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.log_error(
                        "Fehler bei der Job-Registrierung",
                        extra={
                            "job_id": job_id,
                            "job_type": job_type,
                            "status_code": response.status,
                            "error": error_text,
                        },
                    )
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail=f"Job-Manager nicht erreichbar: {error_text}",
                    )
    except aiohttp.ClientError as e:
        logger.log_error("Netzwerkfehler bei der Job-Manager-Kommunikation", error=e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Job-Manager nicht erreichbar: {str(e)}",
        )
    except Exception as e:
        logger.log_error(
            "Unerwarteter Fehler bei der Job-Manager-Kommunikation", error=e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Serverfehler: {str(e)}",
        )


# API-Endpunkte
@app.post(
    "/analyze/videos",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Job erfolgreich erstellt"},
        400: {"description": "Ungültige Anfrage"},
        429: {"description": "Zu viele Anfragen"},
        503: {"description": "Service nicht verfügbar"},
        500: {"description": "Interner Serverfehler"},
    },
)
@limiter.limit("10/minute")
async def analyze_videos(
    request: VideoAnalysisRequest, background_tasks: BackgroundTasks
):
    """
    Analysiert mehrere Videos parallel.

    - **video_paths**: Liste der Video-Pfade
    - **batch_size**: Anzahl der Frames pro Batch (1-32)
    - **frame_sampling_rate**: Jedes n-te Frame wird analysiert (1-10)
    - **priority**: Job-Priorität (1-5)

    Returns:
        JobResponse mit Job-ID und Status
    """
    try:
        logger.log_info(
            "Starte Video-Analyse",
            extra={
                "video_count": len(request.video_paths),
                "batch_size": request.batch_size,
                "frame_sampling_rate": request.frame_sampling_rate,
                "priority": request.priority,
            },
        )

        # Job erstellen
        job_id = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Job in Queue einreihen
        queue.enqueue(
            "job_processor.process_batch_job",
            args=(job_id, request.video_paths, "video"),
            job_id=job_id,
        )

        # Job beim Manager registrieren
        background_tasks.add_task(
            register_job_with_manager, job_id, "video", request.priority
        )

        return JobResponse(
            job_id=job_id,
            status="queued",
            created_at=datetime.now().isoformat(),
            priority=request.priority,
        )

    except ValueError as e:
        logger.log_error("Validierungsfehler bei der Video-Analyse", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.log_error("Unerwarteter Fehler bei der Video-Analyse", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/analyze/images",
    response_model=JobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Job erfolgreich erstellt"},
        400: {"description": "Ungültige Anfrage"},
        429: {"description": "Zu viele Anfragen"},
        503: {"description": "Service nicht verfügbar"},
        500: {"description": "Interner Serverfehler"},
    },
)
@limiter.limit("20/minute")
async def analyze_images(
    request: ImageAnalysisRequest, background_tasks: BackgroundTasks
):
    """
    Analysiert mehrere Bilder parallel.

    - **image_paths**: Liste der Bild-Pfade
    - **batch_size**: Anzahl der Bilder pro Batch (1-32)
    - **priority**: Job-Priorität (1-5)

    Returns:
        JobResponse mit Job-ID und Status
    """
    try:
        logger.log_info(
            "Starte Bild-Analyse",
            extra={
                "image_count": len(request.image_paths),
                "batch_size": request.batch_size,
                "priority": request.priority,
            },
        )

        # Job erstellen
        job_id = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Job in Queue einreihen
        queue.enqueue(
            "job_processor.process_batch_job",
            args=(job_id, request.image_paths, "image"),
            job_id=job_id,
        )

        # Job beim Manager registrieren
        background_tasks.add_task(
            register_job_with_manager, job_id, "image", request.priority
        )

        return JobResponse(
            job_id=job_id,
            status="queued",
            created_at=datetime.now().isoformat(),
            priority=request.priority,
        )

    except ValueError as e:
        logger.log_error("Validierungsfehler bei der Bild-Analyse", error=e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.log_error("Unerwarteter Fehler bei der Bild-Analyse", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get(
    "/jobs/{job_id}",
    response_model=JobStatus,
    responses={
        200: {"description": "Job-Status erfolgreich abgerufen"},
        404: {"description": "Job nicht gefunden"},
        429: {"description": "Zu viele Anfragen"},
        500: {"description": "Interner Serverfehler"},
    },
)
@limiter.limit("60/minute")
async def get_job_status(job_id: str):
    """
    Gibt den Status eines Jobs zurück.

    - **job_id**: Eindeutige Job-ID

    Returns:
        JobStatus mit aktuellem Status und Ergebnissen
    """
    try:
        logger.log_info("Job-Status abrufen", extra={"job_id": job_id})

        # Job aus Redis lesen
        job = queue.fetch_job(job_id)

        if not job:
            logger.log_error("Job nicht gefunden", extra={"job_id": job_id})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job nicht gefunden"
            )

        # Status bestimmen
        job_status = "queued"
        if job.is_finished:
            job_status = "completed"
        elif job.is_failed:
            job_status = "failed"
        elif job.is_started:
            job_status = "processing"

        # Job-Status beim Manager abrufen
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{job_manager_url}/jobs/{job_id}") as response:
                    if response.status == 200:
                        manager_status = await response.json()
                        priority = manager_status.get("priority", 1)
                    else:
                        priority = 1
        except Exception as e:
            logger.log_warning("Konnte Job-Manager-Status nicht abrufen", error=e)
            priority = 1

        return JobStatus(
            job_id=job_id,
            status=job_status,
            created_at=job.created_at.isoformat(),
            updated_at=job.ended_at.isoformat() if job.ended_at else None,
            result=job.result if job.is_finished else None,
            error=str(job.exc_info) if job.is_failed else None,
            priority=priority,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("Fehler beim Abrufen des Job-Status", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.get(
    "/health",
    responses={
        200: {"description": "Service ist gesund"},
        503: {"description": "Service ist beeinträchtigt"},
        500: {"description": "Interner Serverfehler"},
    },
)
@limiter.limit("30/minute")
async def health_check():
    """
    Überprüft den Status des Services.

    Returns:
        Health-Status mit Service-Verfügbarkeit
    """
    try:
        logger.log_info("Health-Check durchgeführt")

        # Service-Status prüfen
        pose_health = await pipeline.pose_estimator.check_service_health()
        ocr_health = await pipeline.ocr_detector.check_service_health()
        nsfw_health = await pipeline.nsfw_detector.check_service_health()

        # Job-Manager-Status prüfen
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{job_manager_url}/health") as response:
                    job_manager_health = response.status == 200
        except Exception as e:
            logger.log_warning("Job-Manager nicht erreichbar", error=e)
            job_manager_health = False

        health_status = {
            "status": (
                "healthy"
                if all([pose_health, ocr_health, nsfw_health, job_manager_health])
                else "degraded"
            ),
            "services": {
                "pose_estimation": pose_health,
                "ocr_detection": ocr_health,
                "nsfw_detection": nsfw_health,
                "job_manager": job_manager_health,
            },
        }

        if health_status["status"] == "degraded":
            logger.log_warning("Service-Status: degraded", extra=health_status)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_status
            )

        return health_status

    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("Fehler beim Health-Check", error=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

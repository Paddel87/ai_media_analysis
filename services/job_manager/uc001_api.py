"""
UC-001 Enhanced Manual Analysis - FastAPI Integration
Version: 1.0.0 - RESTful API für Pipeline-Orchestrierung
Status: ALPHA 0.6.0 - Power-User-First Strategy
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import UC-001 Pipeline Orchestrator
pipeline_available = False
UC001PipelineOrchestrator: Any = None  # type: ignore
UC001PipelineRequest: Any = None  # type: ignore

try:
    from uc001_pipeline import (
        UC001PipelineOrchestrator as _PipelineOrchestrator,
        UC001PipelineRequest as _PipelineRequest,
        UC001PipelineResult,
        UC001JobType as PipelineJobType,
        UC001Priority as PipelinePriority,
        UC001Status as PipelineStatus
    )
    UC001PipelineOrchestrator = _PipelineOrchestrator  # type: ignore
    UC001PipelineRequest = _PipelineRequest  # type: ignore
    pipeline_available = True
except ImportError as e:
    print(f"❌ UC-001 Pipeline module not found: {e}")
    pipeline_available = False

    # Create mock classes for development
    class UC001PipelineOrchestrator:
        pass

    class UC001PipelineRequest:
        pass

# Define API enums (always available)
class UC001JobType:
    FULL_PIPELINE = "full_pipeline"
    PERSON_ANALYSIS = "person_analysis"
    VIDEO_CONTEXT = "video_context"
    CLOTHING_ANALYSIS = "clothing_analysis"

class UC001Priority:
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class UC001Status:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uc001_api")

# ===================================================================
# UC-001 API MODELS
# ===================================================================

class UC001JobSubmissionRequest(BaseModel):
    """Request model for UC-001 job submission."""
    job_type: str  # Use str instead of enum for better compatibility
    media_path: str
    person_id: Optional[str] = None
    analysis_config: Dict[str, str] = Field(default_factory=dict)
    priority: str = "normal"  # Use str instead of enum
    user_id: str
    create_dossier: bool = True
    update_existing: bool = True
    enable_clothing_analysis: bool = True
    enable_video_context: bool = True
    enable_corrections: bool = True
    research_mode: bool = True

class UC001JobStatusResponse(BaseModel):
    """Response model for UC-001 job status."""
    job_id: str
    status: str
    progress: Optional[float] = None
    created_at: str
    updated_at: Optional[str] = None
    estimated_completion: Optional[str] = None
    current_step: Optional[str] = None
    error_message: Optional[str] = None

class UC001PipelineHealthResponse(BaseModel):
    """Response model for UC-001 pipeline health."""
    pipeline_status: str
    services: Dict[str, Dict[str, str]]
    active_jobs: int
    queue_size: int
    max_concurrent: int
    research_mode: bool
    power_user_mode: bool
    timestamp: str

# ===================================================================
# LIFECYCLE MANAGEMENT
# ===================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern FastAPI lifespan management."""
    # Startup
    logger.info("🚀 UC-001 Job Manager API starting...")

    if pipeline_available:
        try:
            # Initialize orchestrator services
            await app.state.orchestrator.init_services()

            # Start background job processing
            asyncio.create_task(app.state.orchestrator.process_job_queue())

            logger.info("✅ UC-001 Job Manager API ready")
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
    else:
        logger.warning("⚠️ UC-001 Pipeline not available - running in mock mode")

    yield

    # Shutdown
    logger.info("🛑 UC-001 Job Manager API shutting down...")

# ===================================================================
# FASTAPI APPLICATION
# ===================================================================

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="UC-001 Enhanced Manual Analysis - Job Manager",
    description="Pipeline-Orchestrierung für Enhanced Manual Analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize UC-001 Pipeline Orchestrator
if pipeline_available:
    app.state.orchestrator = UC001PipelineOrchestrator()
else:
    app.state.orchestrator = None

# ===================================================================
# HEALTH CHECK ENDPOINTS
# ===================================================================

@app.get("/health", response_model=UC001PipelineHealthResponse)
async def health_check():
    """Health check endpoint for UC-001 pipeline."""
    if not pipeline_available or not app.state.orchestrator:
        return UC001PipelineHealthResponse(
            pipeline_status="degraded",
            services={},
            active_jobs=0,
            queue_size=0,
            max_concurrent=4,
            research_mode=True,
            power_user_mode=True,
            timestamp=datetime.now().isoformat()
        )

    health_data = await app.state.orchestrator.get_pipeline_health()
    return UC001PipelineHealthResponse(**health_data)

@app.get("/health/uc001")
async def uc001_health_check():
    """UC-001 specific health check."""
    if not pipeline_available or not app.state.orchestrator:
        return {
            "status": "degraded",
            "uc001_enabled": False,
            "pipeline_ready": False,
            "services_healthy": False,
            "research_mode": True,
            "power_user_mode": True,
            "pipeline_available": pipeline_available,
            "timestamp": datetime.now().isoformat()
        }

    try:
        health_data = await app.state.orchestrator.get_pipeline_health()

        # Determine overall health
        all_services_healthy = all(
            service_info.get("status") == "healthy"
            for service_info in health_data["services"].values()
        )

        return {
            "status": "healthy" if all_services_healthy else "degraded",
            "uc001_enabled": True,
            "pipeline_ready": health_data["pipeline_status"] == "healthy",
            "services_healthy": all_services_healthy,
            "research_mode": health_data["research_mode"],
            "power_user_mode": health_data["power_user_mode"],
            "pipeline_available": pipeline_available,
            "timestamp": health_data["timestamp"]
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "error",
            "uc001_enabled": False,
            "pipeline_ready": False,
            "services_healthy": False,
            "research_mode": True,
            "power_user_mode": True,
            "pipeline_available": pipeline_available,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ===================================================================
# UC-001 JOB MANAGEMENT ENDPOINTS
# ===================================================================

@app.post("/uc001/jobs/submit")
async def submit_uc001_job(request: UC001JobSubmissionRequest) -> Dict[str, str]:
    """
    Submit UC-001 Enhanced Manual Analysis job.

    Unterstützte Job-Typen:
    - full_pipeline: Vollständige Analyse (Person + Video + Kleidung)
    - person_analysis: Nur Personen-Erkennung und Dossier
    - video_context: Nur Video-Kontext-Analyse
    - clothing_analysis: Nur Kleidungsanalyse
    """
    if not pipeline_available or not app.state.orchestrator:
        raise HTTPException(
            status_code=503,
            detail="UC-001 Pipeline not available - running in mock mode"
        )

    try:
        # Convert to pipeline request using dynamic class
        if UC001PipelineRequest:
            try:
                pipeline_request = UC001PipelineRequest(**{
                    "job_type": request.job_type,
                    "media_path": request.media_path,
                    "person_id": request.person_id,
                    "analysis_config": request.analysis_config,
                    "priority": request.priority,
                    "user_id": request.user_id,
                    "create_dossier": request.create_dossier,
                    "update_existing": request.update_existing,
                    "enable_clothing_analysis": request.enable_clothing_analysis,
                    "enable_video_context": request.enable_video_context,
                    "enable_corrections": request.enable_corrections,
                    "research_mode": request.research_mode
                })

                # Submit job
                job_id = await app.state.orchestrator.submit_job(pipeline_request)

                logger.info(f"✅ UC-001 Job submitted: {job_id}")

                return {
                    "job_id": job_id,
                    "status": "submitted",
                    "message": f"UC-001 job {job_id} submitted successfully"
                }
            except TypeError as te:
                logger.error(f"❌ Pipeline request creation failed: {te}")
                raise HTTPException(status_code=500, detail=f"Pipeline request error: {te}")
        else:
            raise HTTPException(status_code=503, detail="Pipeline classes not available")

    except Exception as e:
        logger.error(f"❌ Failed to submit UC-001 job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uc001/jobs/{job_id}/status", response_model=UC001JobStatusResponse)
async def get_uc001_job_status(job_id: str):
    """Get UC-001 job status and progress."""
    if not pipeline_available or not app.state.orchestrator:
        raise HTTPException(
            status_code=503,
            detail="UC-001 Pipeline not available"
        )

    try:
        job_data = await app.state.orchestrator.get_job_status(job_id)

        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        # Calculate progress based on completed steps
        progress = None
        current_step = None

        if "step_results" in job_data:
            total_steps = len(job_data.get("pipeline_steps", []))
            completed_steps = len(job_data["step_results"])

            if total_steps > 0:
                progress = (completed_steps / total_steps) * 100

            # Get current step
            if job_data.get("status") == "processing":
                completed_step_ids = list(job_data["step_results"].keys())
                all_step_ids = [step.get("step_id") for step in job_data.get("pipeline_steps", [])]

                for step_id in all_step_ids:
                    if step_id not in completed_step_ids:
                        current_step = step_id
                        break

        # Extract error message
        error_message = None
        if job_data.get("error_log"):
            latest_error = job_data["error_log"][-1]
            error_message = latest_error.get("error")

        return UC001JobStatusResponse(
            job_id=job_id,
            status=job_data.get("status", "unknown"),
            progress=progress,
            created_at=job_data.get("created_at", ""),
            updated_at=job_data.get("updated_at"),
            current_step=current_step,
            error_message=error_message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uc001/jobs/{job_id}/results")
async def get_uc001_job_results(job_id: str):
    """Get detailed UC-001 job results."""
    try:
        job_data = await app.state.orchestrator.get_job_status(job_id)

        if not job_data:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        if job_data.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Job {job_id} not completed yet (status: {job_data.get('status')})"
            )

        return {
            "job_id": job_id,
            "status": job_data.get("status"),
            "person_id": job_data.get("person_id"),
            "analysis_results": job_data.get("analysis_results", {}),
            "step_results": job_data.get("step_results", {}),
            "quality_metrics": job_data.get("quality_metrics", {}),
            "pipeline_duration": job_data.get("pipeline_duration"),
            "dossier_updated": job_data.get("dossier_updated", False),
            "user_corrections_needed": job_data.get("user_corrections_needed", []),
            "completed_at": job_data.get("completed_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get job results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/uc001/jobs/{job_id}/cancel")
async def cancel_uc001_job(job_id: str):
    """Cancel UC-001 job if possible."""
    try:
        success = await app.state.orchestrator.cancel_job(job_id)

        if success:
            return {
                "job_id": job_id,
                "status": "cancelled",
                "message": f"Job {job_id} cancelled successfully"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to cancel job {job_id} (may already be completed or running)"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uc001/jobs")
async def list_uc001_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs to return")
):
    """List UC-001 jobs with optional filtering."""
    try:
        # Convert status string to enum if provided
        status_filter = None
        if status:
            try:
                status_filter = UC001Status(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        jobs = await app.state.orchestrator.list_jobs(
            status=status_filter,
            user_id=user_id,
            limit=limit
        )

        return {
            "jobs": jobs,
            "total_count": len(jobs),
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================================
# UC-001 PIPELINE MONITORING ENDPOINTS
# ===================================================================

@app.get("/uc001/pipeline/status")
async def get_uc001_pipeline_status():
    """Get comprehensive UC-001 pipeline status."""
    try:
        health_data = await app.state.orchestrator.get_pipeline_health()

        # Add additional pipeline metrics
        active_jobs_by_status = {}
        for job_data in app.state.orchestrator.active_jobs.values():
            status = job_data.get("status", "unknown")
            active_jobs_by_status[status] = active_jobs_by_status.get(status, 0) + 1

        return {
            **health_data,
            "active_jobs_by_status": active_jobs_by_status,
            "service_endpoints": {
                name: {"url": service.url, "port": service.port}
                for name, service in app.state.orchestrator.services.items()
            }
        }

    except Exception as e:
        logger.error(f"❌ Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/uc001/pipeline/metrics")
async def get_uc001_pipeline_metrics():
    """Get UC-001 pipeline performance metrics."""
    try:
        # Calculate metrics from active and recent jobs
        total_jobs = len(app.state.orchestrator.active_jobs)

        # Get recent job statistics
        recent_jobs = await app.state.orchestrator.list_jobs(limit=100)

        completed_jobs = [job for job in recent_jobs if job.get("status") == "completed"]
        failed_jobs = [job for job in recent_jobs if job.get("status") == "failed"]

        # Calculate average pipeline duration
        avg_duration = 0
        if completed_jobs:
            durations = [job.get("pipeline_duration", 0) for job in completed_jobs]
            avg_duration = sum(durations) / len(durations)

        # Calculate success rate
        success_rate = 0
        if recent_jobs:
            success_rate = len(completed_jobs) / len(recent_jobs)

        return {
            "total_jobs_processed": len(recent_jobs),
            "completed_jobs": len(completed_jobs),
            "failed_jobs": len(failed_jobs),
            "success_rate": success_rate,
            "average_pipeline_duration": avg_duration,
            "active_jobs": total_jobs,
            "queue_size": await app.state.orchestrator.redis_client.zcard("uc001:job_queue") if app.state.orchestrator.redis_client else 0,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to get pipeline metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================================================================
# UC-001 CONVENIENCE ENDPOINTS
# ===================================================================

@app.post("/uc001/analyze/full")
async def analyze_full_uc001(
    media_path: str,
    user_id: str,
    person_id: Optional[str] = None,
    priority: UC001Priority = UC001Priority.NORMAL
):
    """
    Convenience endpoint for full UC-001 Enhanced Manual Analysis.

    Führt vollständige Pipeline aus:
    - Personen-Erkennung und Dossier-Management
    - Video-Kontext-Analyse mit LLM
    - Kleidungsanalyse (200+ Kategorien)
    - Benutzer-Korrektur-Integration
    """
    request = UC001JobSubmissionRequest(
        job_type=UC001JobType.FULL_PIPELINE,
        media_path=media_path,
        person_id=person_id,
        user_id=user_id,
        priority=priority,
        research_mode=True,
        enable_clothing_analysis=True,
        enable_video_context=True,
        enable_corrections=True
    )

    return await submit_uc001_job(request)

@app.post("/uc001/analyze/person")
async def analyze_person_uc001(
    media_path: str,
    user_id: str,
    person_id: Optional[str] = None
):
    """Convenience endpoint for person-only analysis."""
    request = UC001JobSubmissionRequest(
        job_type=UC001JobType.PERSON_ANALYSIS,
        media_path=media_path,
        person_id=person_id,
        user_id=user_id,
        research_mode=True,
        create_dossier=True,
        update_existing=True
    )

    return await submit_uc001_job(request)

@app.post("/uc001/analyze/clothing")
async def analyze_clothing_uc001(
    media_path: str,
    user_id: str,
    person_id: Optional[str] = None
):
    """Convenience endpoint for clothing-only analysis."""
    request = UC001JobSubmissionRequest(
        job_type=UC001JobType.CLOTHING_ANALYSIS,
        media_path=media_path,
        person_id=person_id,
        user_id=user_id,
        research_mode=True,
        enable_clothing_analysis=True
    )

    return await submit_uc001_job(request)

# ===================================================================
# DEVELOPMENT & DEBUGGING ENDPOINTS
# ===================================================================

@app.get("/uc001/debug/services")
async def debug_uc001_services():
    """Debug endpoint to check UC-001 service connectivity."""
    service_status = await app.state.orchestrator.validate_uc001_services()
    return {
        "services": service_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/uc001/debug/queue")
async def debug_uc001_queue():
    """Debug endpoint to inspect UC-001 job queue."""
    if not app.state.orchestrator.redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")

    # Get queue contents
    queue_items = await app.state.orchestrator.redis_client.zrange(
        "uc001:job_queue",
        0, -1,
        withscores=True
    )

    return {
        "queue_size": len(queue_items),
        "queue_items": [
            {"job_id": item[0], "priority_score": item[1]}
            for item in queue_items
        ],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "uc001_api:app",
        host="0.0.0.0",
        port=8012,
        log_level="info",
        reload=False
    )

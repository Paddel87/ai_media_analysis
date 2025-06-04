"""
UC-001 Enhanced Manual Analysis - Pipeline Orchestrierung
Version: 1.0.0 - Pipeline-Orchestrierung für Enhanced Manual Analysis
Status: ALPHA 0.6.0 - Power-User-First Strategy
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import time

import httpx
import redis.asyncio as redis
from pydantic import BaseModel, Field
from rich.console import Console
from loguru import logger

# UC-001 Data Schema Integration
try:
    from data_schema.person_dossier import PersonDossier, MediaAppearance
except ImportError:
    logger.warning("Data schema not found. Using local schemas.")

# Initialize Rich Console for Power-User output
console = Console()

# ===================================================================
# UC-001 PIPELINE MODELS & ENUMS
# ===================================================================

class UC001JobType(str, Enum):
    """UC-001 job types for Enhanced Manual Analysis."""
    PERSON_ANALYSIS = "person_analysis"
    VIDEO_CONTEXT = "video_context"
    CLOTHING_ANALYSIS = "clothing_analysis"
    FULL_PIPELINE = "full_pipeline"
    DOSSIER_UPDATE = "dossier_update"
    RE_IDENTIFICATION = "re_identification"
    CORRECTION_PROCESSING = "correction_processing"

class UC001Priority(str, Enum):
    """UC-001 job priorities."""
    CRITICAL = "critical"      # Research-critical analysis
    HIGH = "high"             # Power-user requests
    NORMAL = "normal"         # Standard analysis
    LOW = "low"              # Batch processing
    BACKGROUND = "background"  # Maintenance tasks

class UC001Status(str, Enum):
    """UC-001 job status tracking."""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    WAITING_USER = "waiting_user"  # User correction needed
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class UC001ServiceEndpoint:
    """UC-001 service endpoint configuration."""
    name: str
    url: str
    port: int
    health_endpoint: str
    timeout: int = 300
    required: bool = True

@dataclass
class UC001JobStep:
    """Individual step in UC-001 pipeline."""
    step_id: str
    service: str
    endpoint: str
    input_data: Dict[str, Any]
    depends_on: List[str]
    optional: bool = False
    timeout: int = 300
    retry_count: int = 3

class UC001PipelineRequest(BaseModel):
    """Request for UC-001 pipeline processing."""
    job_type: UC001JobType
    media_path: str
    person_id: Optional[str] = None
    analysis_config: Dict[str, Any] = Field(default_factory=dict)
    priority: UC001Priority = UC001Priority.NORMAL
    user_id: str
    create_dossier: bool = True
    update_existing: bool = True
    enable_clothing_analysis: bool = True
    enable_video_context: bool = True
    enable_corrections: bool = True
    research_mode: bool = True  # Power-User unrestricted mode

class UC001PipelineResult(BaseModel):
    """Result from UC-001 pipeline processing."""
    job_id: str
    status: UC001Status
    person_id: Optional[str] = None
    analysis_results: Dict[str, Any]
    pipeline_duration: float
    step_results: Dict[str, Any]
    quality_metrics: Dict[str, float]
    user_corrections_needed: List[str]
    dossier_updated: bool
    created_at: str
    completed_at: Optional[str] = None

# ===================================================================
# UC-001 PIPELINE ORCHESTRATOR
# ===================================================================

class UC001PipelineOrchestrator:
    """
    UC-001 Enhanced Manual Analysis Pipeline Orchestrator

    Koordiniert alle UC-001 Services für Power-User-Workflows:
    - Person Dossier Management
    - Video Context Analysis
    - Clothing Analysis (200+ Kategorien)
    - User Correction Integration
    - Research-Grade Output Quality
    """

    def __init__(self):
        self.console = Console()
        self.redis_client = None
        self.active_jobs: Dict[str, Dict] = {}
        self.job_history: Dict[str, List] = {}

        # UC-001 Configuration
        self.uc001_enabled = os.getenv("UC001_ENABLED", "true").lower() == "true"
        self.research_mode = os.getenv("UC001_RESEARCH_MODE", "true").lower() == "true"
        self.max_concurrent_jobs = int(os.getenv("UC001_MAX_CONCURRENT", "5"))
        self.power_user_mode = os.getenv("UC001_POWER_USER", "true").lower() == "true"

        # Service Endpoints (UC-001 Services)
        self.services = {
            "person_dossier": UC001ServiceEndpoint(
                name="person_dossier",
                url=os.getenv("PERSON_DOSSIER_URL", "http://ai_person_dossier:8000"),
                port=8000,
                health_endpoint="/health"
            ),
            "video_context_analyzer": UC001ServiceEndpoint(
                name="video_context_analyzer",
                url=os.getenv("VIDEO_CONTEXT_URL", "http://ai_video_context_analyzer:8000"),
                port=8000,
                health_endpoint="/health"
            ),
            "clothing_analyzer": UC001ServiceEndpoint(
                name="clothing_analyzer",
                url=os.getenv("CLOTHING_ANALYZER_URL", "http://ai_clothing_analyzer:8000"),
                port=8000,
                health_endpoint="/health"
            )
        }

        # Pipeline Templates für verschiedene UC-001 Workflows
        self.pipeline_templates = self._initialize_pipeline_templates()

        logger.info(f"🚀 UC-001 Pipeline Orchestrator initialized")
        logger.info(f"🔬 Research Mode: {self.research_mode}")
        logger.info(f"⚡ Power User Mode: {self.power_user_mode}")
        logger.info(f"📊 Max Concurrent Jobs: {self.max_concurrent_jobs}")

    def _initialize_pipeline_templates(self) -> Dict[str, List[UC001JobStep]]:
        """Initialize pipeline templates for different UC-001 workflows."""
        templates = {}

        # Full Pipeline Template (Power-User Research Workflow)
        templates["full_pipeline"] = [
            UC001JobStep(
                step_id="person_detection",
                service="person_dossier",
                endpoint="/detect_person",
                input_data={},
                depends_on=[],
                timeout=120
            ),
            UC001JobStep(
                step_id="video_context_analysis",
                service="video_context_analyzer",
                endpoint="/analyze_context",
                input_data={},
                depends_on=["person_detection"],
                timeout=300
            ),
            UC001JobStep(
                step_id="clothing_analysis",
                service="clothing_analyzer",
                endpoint="/analyze",
                input_data={},
                depends_on=["person_detection"],
                timeout=180
            ),
            UC001JobStep(
                step_id="dossier_integration",
                service="person_dossier",
                endpoint="/update_dossier",
                input_data={},
                depends_on=["video_context_analysis", "clothing_analysis"],
                timeout=60
            )
        ]

        # Person Analysis Only
        templates["person_analysis"] = [
            UC001JobStep(
                step_id="person_detection",
                service="person_dossier",
                endpoint="/detect_person",
                input_data={},
                depends_on=[],
                timeout=120
            ),
            UC001JobStep(
                step_id="dossier_update",
                service="person_dossier",
                endpoint="/update_dossier",
                input_data={},
                depends_on=["person_detection"],
                timeout=60
            )
        ]

        # Video Context Only
        templates["video_context"] = [
            UC001JobStep(
                step_id="context_analysis",
                service="video_context_analyzer",
                endpoint="/analyze_context",
                input_data={},
                depends_on=[],
                timeout=300
            )
        ]

        # Clothing Analysis Only
        templates["clothing_analysis"] = [
            UC001JobStep(
                step_id="clothing_detection",
                service="clothing_analyzer",
                endpoint="/analyze",
                input_data={},
                depends_on=[],
                timeout=180
            )
        ]

        return templates

    async def init_services(self):
        """Initialize Redis and validate UC-001 service connections."""
        await asyncio.gather(
            self.init_redis(),
            self.validate_uc001_services()
        )

    async def init_redis(self):
        """Initialize Redis connection for job coordination."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ UC-001 Redis connection established")
        except Exception as e:
            logger.error(f"❌ UC-001 Redis connection failed: {e}")
            self.redis_client = None

    async def validate_uc001_services(self):
        """Validate all UC-001 services are healthy and accessible."""
        service_status = {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, service in self.services.items():
                try:
                    response = await client.get(f"{service.url}{service.health_endpoint}")
                    if response.status_code == 200:
                        health_data = response.json()
                        service_status[service_name] = {
                            "status": "healthy",
                            "details": health_data
                        }
                        logger.info(f"✅ {service_name}: {health_data.get('status', 'unknown')}")
                    else:
                        service_status[service_name] = {"status": "unhealthy", "code": response.status_code}
                        logger.warning(f"⚠️ {service_name}: HTTP {response.status_code}")

                except Exception as e:
                    service_status[service_name] = {"status": "unreachable", "error": str(e)}
                    logger.error(f"❌ {service_name}: {e}")

        # Cache service status in Redis
        if self.redis_client:
            await self.redis_client.setex(
                "uc001:service_status",
                300,  # 5 minute cache
                json.dumps(service_status)
            )

        return service_status

    async def submit_job(self, request: UC001PipelineRequest) -> str:
        """
        Submit UC-001 pipeline job for processing.

        Returns job_id for tracking.
        """
        start_time = datetime.now()
        job_id = f"uc001_{int(start_time.timestamp())}_{uuid.uuid4().hex[:8]}"

        logger.info(f"🎯 UC-001 Job submitted: {job_id}")
        logger.info(f"📝 Type: {request.job_type}, Priority: {request.priority}")
        logger.info(f"🎥 Media: {Path(request.media_path).name}")

        # Create job entry
        job_data = {
            "job_id": job_id,
            "job_type": request.job_type.value,
            "media_path": request.media_path,
            "person_id": request.person_id,
            "analysis_config": request.analysis_config,
            "priority": request.priority.value,
            "user_id": request.user_id,
            "create_dossier": request.create_dossier,
            "update_existing": request.update_existing,
            "enable_clothing_analysis": request.enable_clothing_analysis,
            "enable_video_context": request.enable_video_context,
            "enable_corrections": request.enable_corrections,
            "research_mode": request.research_mode,
            "status": UC001Status.PENDING.value,
            "created_at": start_time.isoformat(),
            "pipeline_steps": [],
            "step_results": {},
            "error_log": [],
            "user_corrections_needed": []
        }

        # Store in Redis for coordination
        if self.redis_client:
            await self.redis_client.setex(
                f"uc001:job:{job_id}",
                86400,  # 24 hour job retention
                json.dumps(job_data)
            )

            # Add to priority queue
            priority_score = self._calculate_priority_score(request.priority)
            await self.redis_client.zadd(
                "uc001:job_queue",
                {job_id: priority_score}
            )

        # Add to active jobs
        self.active_jobs[job_id] = job_data

        logger.info(f"✅ UC-001 Job {job_id} queued successfully")
        return job_id

    def _calculate_priority_score(self, priority: UC001Priority) -> float:
        """Calculate numeric priority score for Redis sorted set."""
        priority_scores = {
            UC001Priority.CRITICAL: 1.0,
            UC001Priority.HIGH: 2.0,
            UC001Priority.NORMAL: 3.0,
            UC001Priority.LOW: 4.0,
            UC001Priority.BACKGROUND: 5.0
        }
        return priority_scores.get(priority, 3.0)

    async def process_job_queue(self):
        """Background task to process UC-001 job queue."""
        while True:
            try:
                if len(self.active_jobs) >= self.max_concurrent_jobs:
                    await asyncio.sleep(5)
                    continue

                if self.redis_client:
                    # Get highest priority job
                    job_data = await self.redis_client.zpopmin("uc001:job_queue", 1)
                    if job_data:
                        job_id = job_data[0][0]  # Extract job_id from Redis result

                        # Get job details
                        job_json = await self.redis_client.get(f"uc001:job:{job_id}")
                        if job_json:
                            job_details = json.loads(job_json)

                            # Process job asynchronously
                            asyncio.create_task(self.execute_pipeline(job_details))

                await asyncio.sleep(1)  # Check queue every second

            except Exception as e:
                logger.error(f"❌ UC-001 job queue error: {e}")
                await asyncio.sleep(5)

    async def execute_pipeline(self, job_data: Dict) -> UC001PipelineResult:
        """
        Execute UC-001 pipeline for a specific job.
        """
        job_id = job_data["job_id"]
        job_type = job_data["job_type"]
        start_time = datetime.now()

        logger.info(f"🚀 UC-001 Pipeline execution started: {job_id}")

        try:
            # Update job status
            await self._update_job_status(job_id, UC001Status.PROCESSING)

            # Get pipeline template
            pipeline_steps = self.pipeline_templates.get(job_type, [])
            if not pipeline_steps:
                raise ValueError(f"Unknown job type: {job_type}")

            # Execute pipeline steps
            step_results = {}
            analysis_results = {}

            for step in pipeline_steps:
                # Check dependencies
                if not await self._check_step_dependencies(step, step_results):
                    logger.warning(f"⏭️ Skipping step {step.step_id} - dependencies not met")
                    continue

                # Execute step
                step_result = await self._execute_pipeline_step(job_data, step, step_results)
                step_results[step.step_id] = step_result

                # Merge results
                if step_result.get("success"):
                    analysis_results.update(step_result.get("data", {}))

            # Calculate pipeline duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Create result
            result = UC001PipelineResult(
                job_id=job_id,
                status=UC001Status.COMPLETED,
                person_id=analysis_results.get("person_id"),
                analysis_results=analysis_results,
                pipeline_duration=duration,
                step_results=step_results,
                quality_metrics=self._calculate_quality_metrics(step_results),
                user_corrections_needed=job_data.get("user_corrections_needed", []),
                dossier_updated=analysis_results.get("dossier_updated", False),
                created_at=job_data["created_at"],
                completed_at=end_time.isoformat()
            )

            # Update job with final results
            await self._update_job_completion(job_id, result)

            logger.info(f"✅ UC-001 Pipeline completed: {job_id} ({duration:.1f}s)")
            return result

        except Exception as e:
            logger.error(f"❌ UC-001 Pipeline failed: {job_id} - {e}")
            await self._update_job_status(job_id, UC001Status.FAILED, str(e))
            raise

        finally:
            # Remove from active jobs
            self.active_jobs.pop(job_id, None)

    async def _check_step_dependencies(self, step: UC001JobStep, completed_steps: Dict) -> bool:
        """Check if all step dependencies are satisfied."""
        for dep in step.depends_on:
            if dep not in completed_steps:
                return False
            if not completed_steps[dep].get("success", False):
                if not step.optional:
                    return False
        return True

    async def _execute_pipeline_step(
        self,
        job_data: Dict,
        step: UC001JobStep,
        previous_results: Dict
    ) -> Dict:
        """Execute individual pipeline step."""
        step_start = time.time()

        logger.info(f"🔄 Executing step: {step.step_id} ({step.service})")

        try:
            service = self.services[step.service]

            # Prepare input data
            input_data = {**step.input_data}
            input_data.update({
                "job_id": job_data["job_id"],
                "media_path": job_data["media_path"],
                "person_id": job_data.get("person_id"),
                "analysis_config": job_data["analysis_config"],
                "research_mode": job_data["research_mode"]
            })

            # Add results from previous steps
            for dep in step.depends_on:
                if dep in previous_results:
                    input_data[f"{dep}_result"] = previous_results[dep].get("data", {})

            # Execute service call
            async with httpx.AsyncClient(timeout=step.timeout) as client:
                response = await client.post(
                    f"{service.url}{step.endpoint}",
                    json=input_data
                )

                if response.status_code == 200:
                    result_data = response.json()
                    step_duration = time.time() - step_start

                    logger.info(f"✅ Step completed: {step.step_id} ({step_duration:.1f}s)")

                    return {
                        "success": True,
                        "step_id": step.step_id,
                        "service": step.service,
                        "duration": step_duration,
                        "data": result_data
                    }
                else:
                    raise Exception(f"Service error: HTTP {response.status_code}")

        except Exception as e:
            step_duration = time.time() - step_start
            logger.error(f"❌ Step failed: {step.step_id} - {e}")

            return {
                "success": False,
                "step_id": step.step_id,
                "service": step.service,
                "duration": step_duration,
                "error": str(e)
            }

    def _calculate_quality_metrics(self, step_results: Dict) -> Dict[str, float]:
        """Calculate quality metrics from pipeline results."""
        metrics = {}

        # Overall success rate
        total_steps = len(step_results)
        successful_steps = sum(1 for result in step_results.values() if result.get("success"))
        metrics["success_rate"] = successful_steps / total_steps if total_steps > 0 else 0.0

        # Average processing time per step
        total_duration = sum(result.get("duration", 0) for result in step_results.values())
        metrics["avg_step_duration"] = total_duration / total_steps if total_steps > 0 else 0.0

        # Service-specific metrics
        for step_id, result in step_results.items():
            if result.get("success") and "data" in result:
                data = result["data"]

                # Confidence scores
                if "confidence" in data:
                    metrics[f"{step_id}_confidence"] = data["confidence"]

                # Detection counts
                if "detected_items" in data:
                    metrics[f"{step_id}_detections"] = len(data["detected_items"])

        return metrics

    async def _update_job_status(self, job_id: str, status: UC001Status, error: Optional[str] = None):
        """Update job status in Redis."""
        if self.redis_client:
            job_json = await self.redis_client.get(f"uc001:job:{job_id}")
            if job_json:
                job_data = json.loads(job_json)
                job_data["status"] = status.value
                job_data["updated_at"] = datetime.now().isoformat()

                if error:
                    job_data["error_log"].append({
                        "timestamp": datetime.now().isoformat(),
                        "error": error
                    })

                await self.redis_client.setex(
                    f"uc001:job:{job_id}",
                    86400,
                    json.dumps(job_data)
                )

    async def _update_job_completion(self, job_id: str, result: UC001PipelineResult):
        """Update job with final completion data."""
        if self.redis_client:
            job_json = await self.redis_client.get(f"uc001:job:{job_id}")
            if job_json:
                job_data = json.loads(job_json)
                job_data.update({
                    "status": result.status.value,
                    "completed_at": result.completed_at,
                    "pipeline_duration": result.pipeline_duration,
                    "analysis_results": result.analysis_results,
                    "step_results": result.step_results,
                    "quality_metrics": result.quality_metrics,
                    "person_id": result.person_id,
                    "dossier_updated": result.dossier_updated
                })

                await self.redis_client.setex(
                    f"uc001:job:{job_id}",
                    86400,
                    json.dumps(job_data)
                )

    async def get_job_status(self, job_id: str) -> Optional[Dict]:
        """Get UC-001 job status and results."""
        if self.redis_client:
            job_json = await self.redis_client.get(f"uc001:job:{job_id}")
            if job_json:
                return json.loads(job_json)

        return self.active_jobs.get(job_id)

    async def list_jobs(
        self,
        status: Optional[UC001Status] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """List UC-001 jobs with optional filtering."""
        jobs = []

        if self.redis_client:
            # Get all job keys
            job_keys = await self.redis_client.keys("uc001:job:*")

            for key in job_keys[:limit]:
                job_json = await self.redis_client.get(key)
                if job_json:
                    job_data = json.loads(job_json)

                    # Apply filters
                    if status and job_data.get("status") != status.value:
                        continue
                    if user_id and job_data.get("user_id") != user_id:
                        continue

                    jobs.append(job_data)

        # Sort by created_at descending
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jobs

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel UC-001 job if possible."""
        try:
            # Remove from queue
            if self.redis_client:
                await self.redis_client.zrem("uc001:job_queue", job_id)

            # Update status
            await self._update_job_status(job_id, UC001Status.CANCELLED)

            # Remove from active jobs
            self.active_jobs.pop(job_id, None)

            logger.info(f"❌ UC-001 Job cancelled: {job_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to cancel job {job_id}: {e}")
            return False

    async def get_pipeline_health(self) -> Dict:
        """Get comprehensive UC-001 pipeline health status."""
        service_status = {}

        if self.redis_client:
            cached_status = await self.redis_client.get("uc001:service_status")
            if cached_status:
                service_status = json.loads(cached_status)

        # Queue statistics
        queue_size = 0
        if self.redis_client:
            queue_size = await self.redis_client.zcard("uc001:job_queue")

        return {
            "pipeline_status": "healthy" if self.uc001_enabled else "disabled",
            "services": service_status,
            "active_jobs": len(self.active_jobs),
            "queue_size": queue_size,
            "max_concurrent": self.max_concurrent_jobs,
            "research_mode": self.research_mode,
            "power_user_mode": self.power_user_mode,
            "timestamp": datetime.now().isoformat()
        }

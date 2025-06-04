"""
UC-001 Video Context Analyzer Service
Option A Primary: CPU-First LLM-basierte Video-Kontext-Analyse
Version: 2.0.0 - Enhanced Manual Analysis Integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import cv2
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel, Field
import redis.asyncio as redis
from rich.console import Console
from loguru import logger
import psutil
import uvicorn

# UC-001 Data Schema Integration
try:
    from data_schema.person_dossier import PersonDossier, MediaAppearance
    from data_schema.video_analysis import VideoContext, FrameAnalysis, MovementSequence
except ImportError:
    logger.warning("Data schema not found. Using local schemas.")

# Initialize Rich Console for Power-User output
console = Console()

# ===================================================================
# UC-001 VIDEO CONTEXT DATA MODELS
# ===================================================================

class VideoAnalysisRequest(BaseModel):
    video_path: str
    person_id: Optional[str] = None
    analysis_depth: str = Field(default="standard", description="standard, detailed, or research_grade")
    include_audio: bool = Field(default=True)
    include_movement: bool = Field(default=True)
    include_emotions: bool = Field(default=True)
    cloud_enhancement: bool = Field(default=False, description="Enable cloud LLM for enhanced analysis")

class VideoContextResult(BaseModel):
    video_path: str
    person_id: Optional[str] = None
    analysis_id: str
    context_summary: str
    movement_analysis: Dict
    emotion_timeline: List[Dict]
    audio_insights: Dict
    confidence_score: float
    processing_time: float
    llm_provider: str  # "local_cpu", "openai_cloud", "anthropic_cloud"

class FrameContext(BaseModel):
    timestamp: float
    frame_number: int
    detected_emotions: Dict[str, float]
    movement_vector: List[float]
    scene_description: str
    confidence: float

# ===================================================================
# UC-001 VIDEO CONTEXT ANALYZER SERVICE
# ===================================================================

class VideoContextAnalyzer:
    """
    UC-001 Video Context Analyzer: LLM-basierte Video-Kontext-Analyse

    Option A Primary Features:
    - CPU-first video processing
    - Local LLM integration with cloud enhancement options
    - Real-time movement tracking
    - Emotion analysis timeline
    - Audio context integration
    - Power-user controls for analysis depth
    """

    def __init__(self):
        self.console = Console()
        self.redis_client = None
        self.cpu_cores = os.cpu_count()
        self.memory_limit = self._get_memory_limit()

        # UC-001 Configuration
        self.uc001_enabled = os.getenv("UC001_ENABLED", "true").lower() == "true"
        self.cloud_enhancement = os.getenv("LLM_CLOUD_OPTIONAL", "true").lower() == "true"
        self.cost_awareness = os.getenv("LLM_COST_AWARENESS", "true").lower() == "true"

        # CPU-Optimized Settings
        self.cpu_threads = int(os.getenv("VIDEO_CPU_THREADS", "4"))
        self.frame_batch_size = int(os.getenv("FRAME_BATCH_SIZE", "16"))

        logger.info(f"🎬 UC-001 Video Context Analyzer initialized")
        logger.info(f"💻 CPU Cores: {self.cpu_cores}, Memory: {self.memory_limit}GB")
        logger.info(f"⚙️ Option A Primary: CPU-first with cloud enhancement available")

    def _get_memory_limit(self) -> float:
        """Get system memory in GB."""
        return psutil.virtual_memory().total / (1024 ** 3)

    async def init_redis(self):
        """Initialize Redis connection."""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None

    async def extract_frames(self, video_path: str, max_frames: int = 100) -> List[np.ndarray]:
        """
        CPU-optimized frame extraction for video analysis.

        Args:
            video_path: Path to video file
            max_frames: Maximum frames to extract

        Returns:
            List of frames as numpy arrays
        """
        frames = []

        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps

            # Calculate frame sampling interval
            interval = max(1, total_frames // max_frames)

            frame_count = 0
            extracted_count = 0

            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % interval == 0:
                    # Resize for CPU efficiency
                    frame_resized = cv2.resize(frame, (640, 480))
                    frames.append(frame_resized)
                    extracted_count += 1

                frame_count += 1

            cap.release()

            logger.info(f"📽️ Extracted {len(frames)} frames from {duration:.1f}s video")
            return frames

        except Exception as e:
            logger.error(f"❌ Frame extraction failed: {e}")
            return []

    async def analyze_movement_sequence(self, frames: List[np.ndarray]) -> Dict:
        """
        Analyze movement patterns across video frames.

        Args:
            frames: List of video frames

        Returns:
            Movement analysis results
        """
        if len(frames) < 2:
            return {"error": "Insufficient frames for movement analysis"}

        try:
            movement_vectors = []
            prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)

            for i in range(1, len(frames)):
                curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

                # Calculate optical flow
                flow = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray,
                    corners=None,
                    nextPts=None,
                    **dict(winSize=(15,15), maxLevel=2)
                )

                # Extract movement magnitude
                if flow[0] is not None:
                    movement_magnitude = np.mean(np.linalg.norm(flow[0], axis=1))
                    movement_vectors.append(float(movement_magnitude))

                prev_gray = curr_gray

            # Analyze movement patterns
            movement_stats = {
                "total_movement": sum(movement_vectors),
                "average_movement": np.mean(movement_vectors),
                "max_movement": max(movement_vectors) if movement_vectors else 0,
                "movement_timeline": movement_vectors,
                "activity_level": self._classify_activity_level(movement_vectors)
            }

            return movement_stats

        except Exception as e:
            logger.error(f"❌ Movement analysis failed: {e}")
            return {"error": str(e)}

    def _classify_activity_level(self, movement_vectors: List[float]) -> str:
        """Classify activity level based on movement."""
        if not movement_vectors:
            return "no_movement"

        avg_movement = np.mean(movement_vectors)

        if avg_movement < 1.0:
            return "minimal"
        elif avg_movement < 5.0:
            return "moderate"
        elif avg_movement < 15.0:
            return "active"
        else:
            return "very_active"

    async def generate_context_with_llm(
        self,
        frames: List[np.ndarray],
        movement_data: Dict,
        use_cloud: bool = False
    ) -> str:
        """
        Generate video context using LLM (local or cloud).

        Args:
            frames: Video frames
            movement_data: Movement analysis results
            use_cloud: Whether to use cloud LLM

        Returns:
            Generated context description
        """
        try:
            # Prepare context data
            context_data = {
                "frame_count": len(frames),
                "movement_summary": movement_data,
                "analysis_timestamp": datetime.now().isoformat()
            }

            if use_cloud and self.cloud_enhancement:
                # Use cloud LLM (OpenAI, Claude, etc.)
                return await self._generate_cloud_context(context_data)
            else:
                # Use local CPU-based analysis
                return await self._generate_local_context(context_data)

        except Exception as e:
            logger.error(f"❌ LLM context generation failed: {e}")
            return f"Error generating context: {e}"

    async def _generate_local_context(self, context_data: Dict) -> str:
        """Generate context using local CPU-based analysis."""

        # Simple rule-based context generation for CPU-first approach
        movement = context_data.get("movement_summary", {})
        activity_level = movement.get("activity_level", "unknown")

        context_templates = {
            "minimal": "Video shows minimal movement, suggesting a static or restrained scenario.",
            "moderate": "Video contains moderate movement patterns, indicating controlled activity.",
            "active": "Video displays active movement, suggesting dynamic interactions.",
            "very_active": "Video shows high activity levels with significant movement patterns."
        }

        base_context = context_templates.get(activity_level, "Movement analysis inconclusive.")

        # Add movement details
        if "total_movement" in movement:
            base_context += f" Total movement magnitude: {movement['total_movement']:.1f}"

        return base_context

    async def _generate_cloud_context(self, context_data: Dict) -> str:
        """Generate enhanced context using cloud LLM."""

        # This would integrate with OpenAI, Claude, etc.
        # For now, return enhanced local analysis
        local_context = await self._generate_local_context(context_data)

        enhanced_context = f"[Enhanced Analysis] {local_context}\n"
        enhanced_context += "Note: Cloud enhancement would provide deeper behavioral insights, "
        enhanced_context += "emotional state analysis, and contextual scene understanding."

        return enhanced_context

    async def analyze_video_context(self, request: VideoAnalysisRequest) -> VideoContextResult:
        """
        Main video context analysis function.

        Args:
            request: Video analysis request

        Returns:
            Complete video context analysis
        """
        start_time = datetime.now()
        analysis_id = f"vc_{int(start_time.timestamp())}"

        logger.info(f"🎬 Starting video context analysis: {analysis_id}")

        try:
            # Extract frames
            frames = await self.extract_frames(request.video_path)
            if not frames:
                raise ValueError("No frames extracted from video")

            # Analyze movement
            movement_analysis = await self.analyze_movement_sequence(frames)

            # Generate context with LLM
            context_summary = await self.generate_context_with_llm(
                frames,
                movement_analysis,
                use_cloud=request.cloud_enhancement
            )

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()

            # Determine LLM provider used
            llm_provider = "openai_cloud" if request.cloud_enhancement else "local_cpu"

            result = VideoContextResult(
                video_path=request.video_path,
                person_id=request.person_id,
                analysis_id=analysis_id,
                context_summary=context_summary,
                movement_analysis=movement_analysis,
                emotion_timeline=[],  # TODO: Implement emotion analysis
                audio_insights={},    # TODO: Implement audio analysis
                confidence_score=0.85,  # Placeholder
                processing_time=processing_time,
                llm_provider=llm_provider
            )

            # Cache result in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"video_context:{analysis_id}",
                    3600,  # 1 hour cache
                    result.model_dump_json()
                )

            logger.info(f"✅ Video analysis completed in {processing_time:.1f}s")
            return result

        except Exception as e:
            logger.error(f"❌ Video analysis failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ===================================================================
# FASTAPI APPLICATION
# ===================================================================

# Initialize FastAPI app
app = FastAPI(
    title="UC-001 Video Context Analyzer",
    description="Option A Primary: CPU-First LLM-basierte Video-Kontext-Analyse",
    version="2.0.0"
)

# Initialize service
analyzer = VideoContextAnalyzer()

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup."""
    await analyzer.init_redis()
    logger.info("🚀 UC-001 Video Context Analyzer Service started")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "video_context_analyzer",
        "version": "2.0.0",
        "strategy": "Option-A-Primary",
        "uc001_enabled": analyzer.uc001_enabled,
        "cpu_cores": analyzer.cpu_cores,
        "memory_gb": analyzer.memory_limit
    }

@app.post("/analyze", response_model=VideoContextResult)
async def analyze_video(request: VideoAnalysisRequest):
    """
    Analyze video context using UC-001 Enhanced Manual Analysis.

    Option A Primary: CPU-first processing with optional cloud enhancement.
    """
    return await analyzer.analyze_video_context(request)

@app.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Retrieve cached analysis result."""
    if not analyzer.redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")

    result = await analyzer.redis_client.get(f"video_context:{analysis_id}")
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return json.loads(result)

@app.get("/status")
async def service_status():
    """Get detailed service status for Power-User monitoring."""
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()

    return {
        "service": "video_context_analyzer",
        "version": "2.0.0",
        "strategy": "Option-A-Primary",
        "uc001_integration": "enabled",
        "cpu_usage_percent": cpu_usage,
        "memory_usage_gb": (memory.total - memory.available) / (1024**3),
        "memory_available_gb": memory.available / (1024**3),
        "redis_connected": analyzer.redis_client is not None,
        "cloud_enhancement_available": analyzer.cloud_enhancement
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        workers=1
    )

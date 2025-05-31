import os
import logging
import json
import asyncio
import gc
import torch
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

import redis
from rq import Queue, Worker
from rq.job import Job
from rq.worker import HerokuWorker
import aiohttp
import numpy as np

from vision_pipeline import VisionPipeline
from common.logging_config import ServiceLogger

# Logger konfigurieren
logger = ServiceLogger("vision_pipeline_worker")

# Redis-Verbindung konfigurieren
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_conn = redis.Redis(host=redis_host, port=redis_port)

# Job-Queue erstellen
queue = Queue('vision_pipeline', connection=redis_conn)

# Job-Manager-URL
job_manager_url = os.getenv('JOB_MANAGER_URL', 'http://job_manager_api:8000')

class VisionPipelineWorker(HerokuWorker):
    """Angepasster Worker für die Vision Pipeline."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipeline = VisionPipeline(
            output_dir=os.getenv('OUTPUT_DIR', 'data/output'),
            pose_service_url=os.getenv('POSE_SERVICE_URL'),
            ocr_service_url=os.getenv('OCR_SERVICE_URL'),
            nsfw_service_url=os.getenv('NSFW_SERVICE_URL'),
            batch_size=int(os.getenv('BATCH_SIZE', 4)),
            frame_sampling_rate=int(os.getenv('FRAME_SAMPLING_RATE', 2)),
            max_workers=int(os.getenv('MAX_WORKERS', 4))
        )
        self._current_batch_size = self.pipeline.batch_size
        self._gpu_memory_threshold = 0.8  # 80% GPU-Speicher-Nutzung

    def _adjust_batch_size(self):
        """Passt die Batch-Größe basierend auf GPU-Speicher an."""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated()
            memory_reserved = torch.cuda.memory_reserved()
            total_memory = torch.cuda.get_device_properties(0).total_memory
            
            memory_usage = (memory_allocated + memory_reserved) / total_memory
            
            if memory_usage > self._gpu_memory_threshold:
                self._current_batch_size = max(1, self._current_batch_size // 2)
                logger.log_warning("Batch-Größe reduziert", extra={
                    "new_batch_size": self._current_batch_size,
                    "memory_usage": memory_usage
                })
            elif memory_usage < self._gpu_memory_threshold * 0.5:
                self._current_batch_size = min(
                    self.pipeline.batch_size,
                    self._current_batch_size * 2
                )
                logger.log_info("Batch-Größe erhöht", extra={
                    "new_batch_size": self._current_batch_size,
                    "memory_usage": memory_usage
                })

    def _cleanup_gpu_memory(self):
        """Bereinigt GPU-Speicher."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

async def update_job_status(
    job_id: str,
    status: str,
    progress: Optional[float] = None,
    result: Optional[Dict] = None,
    error: Optional[str] = None
):
    """Aktualisiert den Job-Status beim Job-Manager."""
    try:
        status_data = {
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if progress is not None:
            status_data["progress"] = progress
            
        if result is not None:
            status_data["result"] = result
            
        if error is not None:
            status_data["error"] = error
            
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{job_manager_url}/jobs/{job_id}/status",
                json=status_data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.log_error("Fehler bei der Status-Aktualisierung", extra={
                        "job_id": job_id,
                        "status_code": response.status,
                        "error": error_text
                    })
    except Exception as e:
        logger.log_error("Fehler bei der Job-Manager-Kommunikation", error=e)

def process_video_job(job_id: str, video_path: str) -> Dict:
    """Verarbeitet ein Video-Job."""
    try:
        logger.log_info("Verarbeite Video-Job", extra={
            "job_id": job_id,
            "video_path": video_path
        })
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "processing", progress=0.0))
        
        # Video verarbeiten
        result = worker.pipeline.process_video(video_path)
        
        # Ergebnis speichern
        output_path = os.path.join(
            worker.pipeline.output_dir,
            f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "completed", progress=1.0, result=result))
        
        logger.log_info("Video-Job erfolgreich verarbeitet", extra={
            "job_id": job_id,
            "output_path": output_path
        })
        
        return {
            'status': 'success',
            'job_id': job_id,
            'output_path': output_path,
            'result': result
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.log_error("Fehler bei Video-Job", extra={
            "job_id": job_id,
            "error": error_msg
        })
        
        # Fehler-Status aktualisieren
        asyncio.run(update_job_status(job_id, "failed", error=error_msg))
        
        return {
            'status': 'error',
            'job_id': job_id,
            'error': error_msg
        }
    finally:
        worker._cleanup_gpu_memory()

def process_image_job(job_id: str, image_path: str) -> Dict:
    """Verarbeitet ein Bild-Job."""
    try:
        logger.log_info("Verarbeite Bild-Job", extra={
            "job_id": job_id,
            "image_path": image_path
        })
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "processing", progress=0.0))
        
        # Bild verarbeiten
        result = worker.pipeline.process_image(image_path)
        
        # Ergebnis speichern
        output_path = os.path.join(
            worker.pipeline.output_dir,
            f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "completed", progress=1.0, result=result))
        
        logger.log_info("Bild-Job erfolgreich verarbeitet", extra={
            "job_id": job_id,
            "output_path": output_path
        })
        
        return {
            'status': 'success',
            'job_id': job_id,
            'output_path': output_path,
            'result': result
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.log_error("Fehler bei Bild-Job", extra={
            "job_id": job_id,
            "error": error_msg
        })
        
        # Fehler-Status aktualisieren
        asyncio.run(update_job_status(job_id, "failed", error=error_msg))
        
        return {
            'status': 'error',
            'job_id': job_id,
            'error': error_msg
        }
    finally:
        worker._cleanup_gpu_memory()

def process_batch_job(job_id: str, paths: List[str], job_type: str) -> Dict:
    """Verarbeitet einen Batch-Job."""
    try:
        logger.log_info("Verarbeite Batch-Job", extra={
            "job_id": job_id,
            "path_count": len(paths),
            "job_type": job_type
        })
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "processing", progress=0.0))
        
        # Batch verarbeiten
        if job_type == 'video':
            results = []
            for i, video_path in enumerate(paths):
                try:
                    # Fortschritt berechnen
                    progress = (i / len(paths)) * 0.9  # 90% für Verarbeitung
                    
                    # Status aktualisieren
                    asyncio.run(update_job_status(
                        job_id,
                        "processing",
                        progress=progress,
                        result={"current_file": video_path}
                    ))
                    
                    # Video verarbeiten
                    result = worker.pipeline.process_video(video_path)
                    results.append(result)
                    
                    # GPU-Speicher anpassen
                    worker._adjust_batch_size()
                    
                except Exception as e:
                    logger.log_error("Fehler bei Video-Verarbeitung", extra={
                        "job_id": job_id,
                        "video_path": video_path,
                        "error": str(e)
                    })
                    results.append({
                        "error": str(e),
                        "video_path": video_path
                    })
                    
        else:  # Bilder
            results = []
            for i, image_path in enumerate(paths):
                try:
                    # Fortschritt berechnen
                    progress = (i / len(paths)) * 0.9  # 90% für Verarbeitung
                    
                    # Status aktualisieren
                    asyncio.run(update_job_status(
                        job_id,
                        "processing",
                        progress=progress,
                        result={"current_file": image_path}
                    ))
                    
                    # Bild verarbeiten
                    result = worker.pipeline.process_image(image_path)
                    results.append(result)
                    
                    # GPU-Speicher anpassen
                    worker._adjust_batch_size()
                    
                except Exception as e:
                    logger.log_error("Fehler bei Bild-Verarbeitung", extra={
                        "job_id": job_id,
                        "image_path": image_path,
                        "error": str(e)
                    })
                    results.append({
                        "error": str(e),
                        "image_path": image_path
                    })
        
        # Ergebnis speichern
        output_path = os.path.join(
            worker.pipeline.output_dir,
            f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Status aktualisieren
        asyncio.run(update_job_status(job_id, "completed", progress=1.0, result=results))
        
        logger.log_info("Batch-Job erfolgreich verarbeitet", extra={
            "job_id": job_id,
            "output_path": output_path,
            "result_count": len(results)
        })
        
        return {
            'status': 'success',
            'job_id': job_id,
            'output_path': output_path,
            'result': results
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.log_error("Fehler bei Batch-Job", extra={
            "job_id": job_id,
            "error": error_msg
        })
        
        # Fehler-Status aktualisieren
        asyncio.run(update_job_status(job_id, "failed", error=error_msg))
        
        return {
            'status': 'error',
            'job_id': job_id,
            'error': error_msg
        }
    finally:
        worker._cleanup_gpu_memory()

if __name__ == '__main__':
    # Worker starten
    worker = VisionPipelineWorker([queue], connection=redis_conn)
    worker.work() 
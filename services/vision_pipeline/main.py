import cv2
import numpy as np
import torch
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import hashlib
import sys
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json
import gc
import redis
import pickle
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("vision_pipeline")

class VisionPipeline:
    def __init__(self,
                 output_dir: str = "data/output",
                 pose_service_url: str = "http://pose_estimation:8000",
                 ocr_service_url: str = "http://ocr_detection:8000",
                 nsfw_service_url: str = "http://clip_nsfw:8000",
                 batch_size: int = 4,
                 frame_sampling_rate: int = 2,
                 max_workers: int = 4,
                 cache_size: int = 1000,
                 gpu_memory_threshold: float = 0.8,
                 gpu_cleanup_interval: int = 100):
        """
        Initialisiert die Vision Pipeline mit Performance-Optimierungen.
        
        Args:
            output_dir: Ausgabeverzeichnis für Ergebnisse
            pose_service_url: URL des Pose Estimation Services
            ocr_service_url: URL des OCR Detection Services
            nsfw_service_url: URL des NSFW Detection Services
            batch_size: Optimale Batch-Größe für GPU
            frame_sampling_rate: Jedes n-te Frame wird analysiert
            max_workers: Maximale Anzahl paralleler Worker
            cache_size: Größe des LRU-Caches
            gpu_memory_threshold: GPU-Speicher-Schwellenwert für Batch-Anpassung
            gpu_cleanup_interval: Anzahl der Frames zwischen GPU-Cleanups
        """
        try:
            # Service-URLs
            self.pose_service_url = pose_service_url
            self.ocr_service_url = ocr_service_url
            self.nsfw_service_url = nsfw_service_url
            
            # Konfiguration
            self.output_dir = output_dir
            self.batch_size = batch_size
            self.frame_sampling_rate = frame_sampling_rate
            self.max_workers = max_workers
            self.gpu_memory_threshold = gpu_memory_threshold
            self.gpu_cleanup_interval = gpu_cleanup_interval
            self.frame_counter = 0
            self.last_cleanup_time = datetime.now()
            
            # Thread-Pool für parallele Verarbeitung
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            
            # Redis für Caching
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0))
            )
            
            # Cache für Frame-Hashes
            self._frame_cache = lru_cache(maxsize=cache_size)(self._analyze_frame_internal)
            
            # CUDA-Optimierungen
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                self.device = torch.device("cuda")
                # Setze initiale GPU-Memory-Limits
                torch.cuda.set_per_process_memory_fraction(0.8)  # Maximal 80% GPU-Speicher
                torch.cuda.empty_cache()
            else:
                self.device = torch.device("cpu")
            
            # Ausgabeverzeichnis erstellen
            os.makedirs(output_dir, exist_ok=True)
            
            logger.log_info("Vision Pipeline initialisiert", extra={
                "output_dir": output_dir,
                "batch_size": batch_size,
                "frame_sampling_rate": frame_sampling_rate,
                "max_workers": max_workers,
                "cache_size": cache_size,
                "device": str(self.device)
            })
            
        except Exception as e:
            logger.log_error("Fehler bei der Initialisierung der Vision Pipeline", error=e)
            raise

    def _monitor_gpu_memory(self) -> Dict[str, float]:
        """Überwacht die GPU-Speichernutzung und gibt Metriken zurück."""
        if not torch.cuda.is_available():
            return {"memory_usage": 0.0, "memory_allocated": 0.0, "memory_reserved": 0.0}
            
        memory_allocated = torch.cuda.memory_allocated()
        memory_reserved = torch.cuda.memory_reserved()
        total_memory = torch.cuda.get_device_properties(0).total_memory
        
        return {
            "memory_usage": (memory_allocated + memory_reserved) / total_memory,
            "memory_allocated": memory_allocated / total_memory,
            "memory_reserved": memory_reserved / total_memory
        }

    def _cleanup_gpu_memory(self, force: bool = False):
        """
        Bereinigt GPU-Speicher mit verbesserten Strategien.
        
        Args:
            force: Wenn True, wird der Cleanup erzwungen, unabhängig vom Intervall
        """
        if not torch.cuda.is_available():
            return
            
        current_time = datetime.now()
        time_since_last_cleanup = (current_time - self.last_cleanup_time).total_seconds()
        
        # Cleanup basierend auf Zeit oder Frame-Counter
        if force or (self.frame_counter % self.gpu_cleanup_interval == 0) or (time_since_last_cleanup > 300):  # 5 Minuten
            try:
                # Speichernutzung vor dem Cleanup
                before_metrics = self._monitor_gpu_memory()
                
                # Cache leeren
                torch.cuda.empty_cache()
                gc.collect()
                
                # Temporäre Tensoren freigeben
                for obj in gc.get_objects():
                    try:
                        if torch.is_tensor(obj) and obj.device.type == 'cuda':
                            del obj
                    except:
                        pass
                
                # Speichernutzung nach dem Cleanup
                after_metrics = self._monitor_gpu_memory()
                
                # Logging
                logger.log_info("GPU-Speicher bereinigt", extra={
                    "before_memory_usage": before_metrics["memory_usage"],
                    "after_memory_usage": after_metrics["memory_usage"],
                    "memory_freed": before_metrics["memory_usage"] - after_metrics["memory_usage"],
                    "frame_counter": self.frame_counter
                })
                
                self.last_cleanup_time = current_time
                
            except Exception as e:
                logger.log_error("Fehler beim GPU-Speicher-Cleanup", error=e)

    def _adjust_batch_size(self):
        """Passt die Batch-Größe basierend auf GPU-Speicher an."""
        if not torch.cuda.is_available():
            return
            
        metrics = self._monitor_gpu_memory()
        memory_usage = metrics["memory_usage"]
        
        if memory_usage > self.gpu_memory_threshold:
            # Reduziere Batch-Größe und führe Cleanup durch
            self.batch_size = max(1, self.batch_size // 2)
            self._cleanup_gpu_memory(force=True)
            logger.log_warning("Batch-Größe reduziert", extra={
                "new_batch_size": self.batch_size,
                "memory_usage": memory_usage,
                "memory_allocated": metrics["memory_allocated"],
                "memory_reserved": metrics["memory_reserved"]
            })
        elif memory_usage < self.gpu_memory_threshold * 0.5:
            # Erhöhe Batch-Größe vorsichtig
            self.batch_size = min(32, self.batch_size * 2)
            logger.log_info("Batch-Größe erhöht", extra={
                "new_batch_size": self.batch_size,
                "memory_usage": memory_usage
            })

    def _compute_frame_hash(self, frame: np.ndarray) -> str:
        """Berechnet einen Hash für ein Frame zur Caching-Identifikation."""
        try:
            return hashlib.md5(frame.tobytes()).hexdigest()
        except Exception as e:
            logger.log_error("Fehler beim Berechnen des Frame-Hashes", error=e)
            raise

    async def _analyze_frame_internal(self, frame: np.ndarray) -> Dict[str, Any]:
        """Interne Frame-Analyse mit Caching."""
        try:
            # Frame-Hash für Cache-Lookup
            frame_hash = self._compute_frame_hash(frame)
            
            # Cache prüfen
            cached_result = self.redis_client.get(f"frame:{frame_hash}")
            if cached_result:
                return pickle.loads(cached_result)
            
            # Asynchrone Analyse aller Services
            async with aiohttp.ClientSession() as session:
                tasks = [
                    self._analyze_pose(session, frame),
                    self._analyze_ocr(session, frame),
                    self._analyze_nsfw(session, frame)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Ergebnisse zusammenführen
            result = {
                "pose": results[0] if not isinstance(results[0], Exception) else None,
                "ocr": results[1] if not isinstance(results[1], Exception) else None,
                "nsfw": results[2] if not isinstance(results[2], Exception) else None
            }
            
            # Cache speichern
            self.redis_client.setex(
                f"frame:{frame_hash}",
                3600,  # 1 Stunde TTL
                pickle.dumps(result)
            )
            
            return result
            
        except Exception as e:
            logger.log_error("Fehler bei der Frame-Analyse", error=e)
            raise

    async def process_video(self, video_path: str, job_id: str) -> Dict[str, Any]:
        """
        Verarbeitet ein Video mit optimierter Batch-Verarbeitung.
        
        Args:
            video_path: Pfad zum Video
            job_id: Job-ID für Tracking
            
        Returns:
            Analyseergebnisse
        """
        try:
            logger.log_info("Starte Video-Verarbeitung", extra={
                "video_path": video_path,
                "job_id": job_id
            })
            
            # Video öffnen
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Konnte Video nicht öffnen: {video_path}")
            
            # Video-Metadaten
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps
            
            # Frames sammeln
            frames = []
            frame_numbers = []
            frame_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                if frame_idx % self.frame_sampling_rate == 0:
                    frames.append(frame)
                    frame_numbers.append(frame_idx)
                    
                frame_idx += 1
                
                # Batch-Größe anpassen
                if len(frames) >= self.batch_size:
                    self._adjust_batch_size()
            
            cap.release()
            
            # Frames in Batches aufteilen
            batches = []
            current_batch = []
            
            for frame, frame_number in zip(frames, frame_numbers):
                current_batch.append((frame, frame_number))
                self.frame_counter += 1
                
                # Regelmäßige GPU-Überwachung
                if self.frame_counter % 10 == 0:  # Alle 10 Frames
                    self._adjust_batch_size()
                
                if len(current_batch) >= self.batch_size:
                    batches.append(current_batch)
                    current_batch = []
                    
            if current_batch:
                batches.append(current_batch)
            
            # Asynchrone Batch-Verarbeitung mit verbessertem Memory-Management
            results = []
            for batch_idx, batch in enumerate(batches):
                try:
                    batch_results = await asyncio.gather(*[
                        self._analyze_frame_internal(frame)
                        for frame, _ in batch
                    ])
                    results.extend(batch_results)
                    
                    # Regelmäßiger GPU-Cleanup
                    if batch_idx % 5 == 0:  # Alle 5 Batches
                        self._cleanup_gpu_memory()
                        
                except Exception as e:
                    logger.log_error(f"Fehler bei Batch {batch_idx}", error=e)
                    # Bei Fehler: Cleanup und reduzierte Batch-Größe
                    self._cleanup_gpu_memory(force=True)
                    self.batch_size = max(1, self.batch_size // 2)
                    continue
            
            # Ergebnisse speichern
            output_path = os.path.join(
                self.output_dir,
                f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(output_path, 'w') as f:
                json.dump({
                    "video_path": video_path,
                    "fps": fps,
                    "frame_count": frame_count,
                    "duration": duration,
                    "results": results
                }, f, indent=2)
            
            logger.log_info("Video-Verarbeitung abgeschlossen", extra={
                "video_path": video_path,
                "job_id": job_id,
                "output_path": output_path
            })
            
            return {
                "status": "completed",
                "output_path": output_path,
                "frame_count": frame_count,
                "processed_frames": len(results)
            }
            
        except Exception as e:
            logger.log_error("Fehler bei der Video-Verarbeitung", error=e)
            raise

    async def process_image(self, image_path: str, job_id: str) -> Dict[str, Any]:
        """
        Verarbeitet ein Bild mit optimiertem Caching.
        
        Args:
            image_path: Pfad zum Bild
            job_id: Job-ID für Tracking
            
        Returns:
            Analyseergebnisse
        """
        try:
            logger.log_info("Starte Bild-Verarbeitung", extra={
                "image_path": image_path,
                "job_id": job_id
            })
            
            # Bild laden
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Konnte Bild nicht laden: {image_path}")
            
            # Frame analysieren
            result = await self._analyze_frame_internal(image)
            
            # Ergebnisse speichern
            output_path = os.path.join(
                self.output_dir,
                f"{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(output_path, 'w') as f:
                json.dump({
                    "image_path": image_path,
                    "results": result
                }, f, indent=2)
            
            logger.log_info("Bild-Verarbeitung abgeschlossen", extra={
                "image_path": image_path,
                "job_id": job_id,
                "output_path": output_path
            })
            
            return {
                "status": "completed",
                "output_path": output_path
            }
            
        except Exception as e:
            logger.log_error("Fehler bei der Bild-Verarbeitung", error=e)
            raise

    async def _analyze_pose(self, session: aiohttp.ClientSession, frame: np.ndarray) -> Dict[str, Any]:
        """Analysiert die Pose in einem Frame."""
        try:
            # Frame in Base64 kodieren
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # API-Anfrage
            async with session.post(
                f"{self.pose_service_url}/analyze",
                json={"image_data": frame_base64}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"Pose-Analyse fehlgeschlagen: {response.status}")
                    
        except Exception as e:
            logger.log_error("Fehler bei der Pose-Analyse", error=e)
            raise

    async def _analyze_ocr(self, session: aiohttp.ClientSession, frame: np.ndarray) -> Dict[str, Any]:
        """Analysiert Text in einem Frame."""
        try:
            # Frame in Base64 kodieren
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # API-Anfrage
            async with session.post(
                f"{self.ocr_service_url}/analyze",
                json={"image_data": frame_base64}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"OCR-Analyse fehlgeschlagen: {response.status}")
                    
        except Exception as e:
            logger.log_error("Fehler bei der OCR-Analyse", error=e)
            raise

    async def _analyze_nsfw(self, session: aiohttp.ClientSession, frame: np.ndarray) -> Dict[str, Any]:
        """Analysiert NSFW-Inhalte in einem Frame."""
        try:
            # Frame in Base64 kodieren
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # API-Anfrage
            async with session.post(
                f"{self.nsfw_service_url}/analyze",
                json={"image_data": frame_base64}
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ValueError(f"NSFW-Analyse fehlgeschlagen: {response.status}")
                    
        except Exception as e:
            logger.log_error("Fehler bei der NSFW-Analyse", error=e)
            raise

if __name__ == "__main__":
    # Beispiel-Verwendung
    pipeline = VisionPipeline()
    
    # Mehrere Videos verarbeiten
    video_paths = [
        "/app/data/incoming/video1.mp4",
        "/app/data/incoming/video2.mp4"
    ]
    if all(os.path.exists(path) for path in video_paths):
        results = asyncio.run(pipeline.process_multiple_videos(video_paths))
        print(f"Videos verarbeitet: {len(results)}")
    
    # Mehrere Bilder verarbeiten
    image_paths = [
        "/app/data/incoming/image1.jpg",
        "/app/data/incoming/image2.jpg"
    ]
    if all(os.path.exists(path) for path in image_paths):
        results = asyncio.run(pipeline.process_multiple_images(image_paths))
        print(f"Bilder verarbeitet: {len(results)}") 
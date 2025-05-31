import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import json
import os
from datetime import datetime
import asyncio
from pose import PoseEstimator
from ocr import OCRDetector
from nsfw import NSFWDetector
from restraint_detector import RestraintDetector
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("vision_pipeline")

class VisionPipeline:
    def __init__(self, 
                 output_dir: str = "/app/data/results",
                 pose_service_url: str = "http://pose_estimation:8000",
                 ocr_service_url: str = "http://ocr_detection:8000",
                 nsfw_service_url: str = "http://clip_nsfw:8000",
                 restraint_service_url: str = "http://restraint_detection:8000",
                 batch_size: int = 4,
                 frame_sampling_rate: int = 2,
                 max_workers: int = 4) -> None:
        """
        Initialisiert die Vision Pipeline.
        
        Args:
            output_dir: Verzeichnis für die Ausgabedateien
            pose_service_url: URL des Pose Estimation Services
            ocr_service_url: URL des OCR Services
            nsfw_service_url: URL des CLIP NSFW Services
            restraint_service_url: URL des Restraint Detection Services
            batch_size: Anzahl der Frames pro Batch
            frame_sampling_rate: Jedes n-te Frame wird analysiert
            max_workers: Maximale Anzahl paralleler Worker
        """
        try:
            self.output_dir = output_dir
            self.pose_estimator = PoseEstimator(pose_service_url)
            self.ocr_detector = OCRDetector(ocr_service_url)
            self.nsfw_detector = NSFWDetector(
                nsfw_service_url,
                batch_size=batch_size,
                frame_sampling_rate=frame_sampling_rate
            )
            self.restraint_detector = RestraintDetector(
                restraint_service_url,
                batch_size=batch_size,
                frame_sampling_rate=frame_sampling_rate
            )
            self.max_workers = max_workers
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            self._ensure_output_dir()
            
            logger.log_info("Vision Pipeline initialisiert", extra={
                "output_dir": output_dir,
                "batch_size": batch_size,
                "frame_sampling_rate": frame_sampling_rate,
                "max_workers": max_workers
            })
        except Exception as e:
            logger.log_error("Fehler bei der Initialisierung der Vision Pipeline", error=e)
            raise
        
    def _ensure_output_dir(self) -> None:
        """Stellt sicher, dass das Ausgabeverzeichnis existiert."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def process_multiple_videos(self, video_paths: List[str]) -> List[Dict]:
        """
        Verarbeitet mehrere Videos parallel.
        
        Args:
            video_paths: Liste von Video-Pfaden
            
        Returns:
            Liste von Verarbeitungsergebnissen
        """
        try:
            logger.log_info("Starte Verarbeitung mehrerer Videos", extra={
                "video_count": len(video_paths),
                "video_paths": video_paths
            })
            
            # Frames aus allen Videos sammeln
            all_frames = []
            all_frame_numbers = []
            all_video_indices = []
            video_metadata = []
            
            for video_idx, video_path in enumerate(video_paths):
                try:
                    cap = cv2.VideoCapture(video_path)
                    if not cap.isOpened():
                        logger.log_error(f"Konnte Video nicht öffnen: {video_path}")
                        continue
                        
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    
                    video_metadata.append({
                        "video_path": video_path,
                        "fps": fps,
                        "total_frames": total_frames,
                        "processing_start": datetime.now().isoformat()
                    })
                    
                    frame_count = 0
                    while True:
                        ret, frame = cap.read()
                        if not ret:
                            break
                            
                        if frame_count % self.nsfw_detector.frame_sampling_rate == 0:
                            all_frames.append(frame)
                            all_frame_numbers.append(frame_count)
                            all_video_indices.append(video_idx)
                            
                        frame_count += 1
                        
                    cap.release()
                    
                except Exception as e:
                    logger.log_error(f"Fehler bei der Verarbeitung des Videos {video_path}", error=e)
                    continue
            
            # Frames in Batches aufteilen
            batches = []
            current_batch = []
            current_video_indices = []
            
            for i, (frame, frame_number, video_idx) in enumerate(zip(all_frames, all_frame_numbers, all_video_indices)):
                current_batch.append((frame, frame_number))
                current_video_indices.append(video_idx)
                
                if len(current_batch) >= self.nsfw_detector.batch_size:
                    batches.append((current_batch, current_video_indices))
                    current_batch = []
                    current_video_indices = []
                    
            if current_batch:
                batches.append((current_batch, current_video_indices))
            
            # Batch-Verarbeitung
            results = [{"frames": []} for _ in video_paths]
            
            async with aiohttp.ClientSession() as session:
                for batch, video_indices in batches:
                    frames, frame_numbers = zip(*batch)
                    
                    # NSFW-Analyse
                    nsfw_results = await self.nsfw_detector.process_video_sequence(frames, frame_numbers)
                    
                    # Restraint-Analyse
                    restraint_results = await self.restraint_detector.process_video_sequence(frames, frame_numbers)
                    
                    # Pose und OCR parallel verarbeiten
                    pose_tasks = []
                    ocr_tasks = []
                    
                    for frame, frame_number in batch:
                        pose_tasks.append(self.pose_estimator.process_video_frame(frame, frame_number))
                        ocr_tasks.append(self.ocr_detector.process_video_frame(frame, frame_number))
                    
                    pose_results = await asyncio.gather(*pose_tasks)
                    ocr_results = await asyncio.gather(*ocr_tasks)
                    
                    # Ergebnisse zuordnen
                    for i, (frame_number, nsfw_result, restraint_result, pose_result, ocr_result, video_idx) in enumerate(
                        zip(frame_numbers, nsfw_results, restraint_results, pose_results, ocr_results, video_indices)):
                        
                        frame_result = {
                            "frame_number": frame_number,
                            "timestamp": frame_number / video_metadata[video_idx]["fps"],
                            "pose_data": pose_result["pose_data"],
                            "ocr_data": ocr_result["ocr_data"],
                            "nsfw_data": nsfw_result["nsfw_data"],
                            "restraint_data": restraint_result["restraint_data"],
                            "processing_time": {
                                "pose": pose_result.get("processing_time", 0),
                                "ocr": ocr_result.get("processing_time", 0),
                                "nsfw": nsfw_result.get("processing_time", 0),
                                "restraint": restraint_result.get("processing_time", 0)
                            }
                        }
                        
                        results[video_idx]["frames"].append(frame_result)
                        
            # Metadaten hinzufügen und speichern
            for i, result in enumerate(results):
                result.update(video_metadata[i])
                result["processing_end"] = datetime.now().isoformat()
                self._save_results(result, video_paths[i])
            
            return results
        except Exception as e:
            logger.log_error("Fehler bei der Verarbeitung mehrerer Videos", error=e)
            raise

    async def process_multiple_images(self, image_paths: List[str]) -> List[Dict]:
        """
        Verarbeitet mehrere Bilder parallel.
        
        Args:
            image_paths: Liste von Bild-Pfaden
            
        Returns:
            Liste von Verarbeitungsergebnissen
        """
        # Bilder laden
        images = []
        for path in image_paths:
            frame = cv2.imread(path)
            if frame is not None:
                images.append((frame, path))
            else:
                logger.log_error(f"Konnte Bild nicht laden: {path}")
                
        # Bilder in Batches aufteilen
        batches = []
        current_batch = []
        current_paths = []
        
        for frame, path in images:
            current_batch.append(frame)
            current_paths.append(path)
            
            if len(current_batch) >= self.nsfw_detector.batch_size:
                batches.append((current_batch, current_paths))
                current_batch = []
                current_paths = []
                
        if current_batch:
            batches.append((current_batch, current_paths))
            
        # Batch-Verarbeitung
        results = []
        
        async with aiohttp.ClientSession() as session:
            for batch, paths in batches:
                # NSFW-Analyse
                nsfw_results = await self.nsfw_detector.process_video_sequence(batch, list(range(len(batch))))
                
                # Restraint-Analyse
                restraint_results = await self.restraint_detector.process_video_sequence(batch, list(range(len(batch))))
                
                # Pose und OCR parallel verarbeiten
                pose_tasks = []
                ocr_tasks = []
                
                for frame in batch:
                    pose_tasks.append(self.pose_estimator.analyze_frame(frame))
                    ocr_tasks.append(self.ocr_detector.analyze_frame(frame))
                
                pose_results = await asyncio.gather(*pose_tasks)
                ocr_results = await asyncio.gather(*ocr_tasks)
                
                # Ergebnisse zuordnen
                for i, (path, nsfw_result, restraint_result, pose_result, ocr_result) in enumerate(
                    zip(paths, nsfw_results, restraint_results, pose_results, ocr_results)):
                    
                    result = {
                        "image_path": path,
                        "processing_time": datetime.now().isoformat(),
                        "pose_data": pose_result,
                        "ocr_data": ocr_result,
                        "nsfw_data": nsfw_result["nsfw_data"],
                        "restraint_data": restraint_result["restraint_data"]
                    }
                    
                    results.append(result)
                    self._save_results(result, path)
                    
        return results

    def _save_results(self, results: Dict[str, Any], input_path: str) -> None:
        """
        Speichert die Ergebnisse in einer JSON-Datei.
        
        Args:
            results: Verarbeitungsergebnisse
            input_path: Pfad zur Eingabedatei
        """
        try:
            # Dateinamen generieren
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(self.output_dir, f"{base_name}_results.json")
            
            # Ergebnisse speichern
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            logger.log_info("Ergebnisse erfolgreich gespeichert", extra={
                "input_path": input_path,
                "output_path": output_path
            })
            
        except Exception as e:
            logger.log_error("Fehler beim Speichern der Ergebnisse", error=e, extra={
                "input_path": input_path
            })
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
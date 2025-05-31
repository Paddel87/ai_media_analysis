import cv2
import numpy as np
import logging
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
from pose import PoseEstimator

# Logging-Konfiguration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisionPipeline:
    def __init__(self, 
                 output_dir: str = "/app/data/results",
                 pose_service_url: str = "http://pose_estimation:8000"):
        """
        Initialisiert die Vision Pipeline.
        
        Args:
            output_dir: Verzeichnis für die Ausgabedateien
            pose_service_url: URL des Pose Estimation Services
        """
        self.output_dir = output_dir
        self.pose_estimator = PoseEstimator(pose_service_url)
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        """Stellt sicher, dass das Ausgabeverzeichnis existiert."""
        os.makedirs(self.output_dir, exist_ok=True)
        
    def process_video(self, video_path: str) -> Dict:
        """
        Verarbeitet ein Video durch die Pipeline.
        
        Args:
            video_path: Pfad zum Video
            
        Returns:
            Dict mit den Verarbeitungsergebnissen
        """
        try:
            # Video öffnen
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Konnte Video nicht öffnen: {video_path}")
            
            # Video-Metadaten
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Ergebnisse initialisieren
            results = {
                "video_path": video_path,
                "fps": fps,
                "total_frames": total_frames,
                "processing_start": datetime.now().isoformat(),
                "frames": []
            }
            
            # Frames verarbeiten
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Pose Estimation
                pose_result = self.pose_estimator.process_video_frame(frame, frame_count)
                results["frames"].append(pose_result)
                
                frame_count += 1
                if frame_count % 100 == 0:
                    logger.info(f"Verarbeitete Frames: {frame_count}/{total_frames}")
            
            # Video schließen
            cap.release()
            
            # Ergebnisse speichern
            results["processing_end"] = datetime.now().isoformat()
            self._save_results(results, video_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Video-Verarbeitung: {str(e)}")
            raise
            
    def process_image(self, image_path: str) -> Dict:
        """
        Verarbeitet ein einzelnes Bild.
        
        Args:
            image_path: Pfad zum Bild
            
        Returns:
            Dict mit den Verarbeitungsergebnissen
        """
        try:
            # Bild laden
            frame = cv2.imread(image_path)
            if frame is None:
                raise ValueError(f"Konnte Bild nicht laden: {image_path}")
            
            # Pose Estimation
            pose_result = self.pose_estimator.analyze_frame(frame)
            
            # Ergebnisse zusammenstellen
            results = {
                "image_path": image_path,
                "processing_time": datetime.now().isoformat(),
                "pose_data": pose_result
            }
            
            # Ergebnisse speichern
            self._save_results(results, image_path)
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Bild-Verarbeitung: {str(e)}")
            raise
            
    def _save_results(self, results: Dict, input_path: str):
        """
        Speichert die Ergebnisse in einer JSON-Datei.
        
        Args:
            results: Verarbeitungsergebnisse
            input_path: Pfad zur Eingabedatei
        """
        try:
            # Dateinamen generieren
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"{base_name}_{timestamp}.json")
            
            # JSON speichern
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Ergebnisse gespeichert in: {output_file}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Ergebnisse: {str(e)}")
            raise

if __name__ == "__main__":
    # Beispiel-Verwendung
    pipeline = VisionPipeline()
    
    # Video verarbeiten
    video_path = "/app/data/incoming/example.mp4"
    if os.path.exists(video_path):
        results = pipeline.process_video(video_path)
        print(f"Video verarbeitet: {len(results['frames'])} Frames")
    
    # Bild verarbeiten
    image_path = "/app/data/incoming/example.jpg"
    if os.path.exists(image_path):
        results = pipeline.process_image(image_path)
        print(f"Bild verarbeitet: {results['pose_data']}") 
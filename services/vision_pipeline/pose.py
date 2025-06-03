import logging
from typing import Dict, List

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


class PoseEstimator:
    def __init__(self, pose_service_url: str = "http://pose_estimation:8000"):
        self.pose_service_url = pose_service_url
        self.analyze_endpoint = f"{pose_service_url}/analyze"
        self.health_endpoint = f"{pose_service_url}/health"

    def check_service_health(self) -> bool:
        """Überprüft, ob der Pose Estimation Service verfügbar ist."""
        try:
            response = requests.get(self.health_endpoint)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Pose Estimation Service nicht erreichbar: {str(e)}")
            return False

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analysiert ein einzelnes Frame auf Körperhaltungen.

        Args:
            frame: NumPy Array des Bildes (BGR Format)

        Returns:
            Dict mit den erkannten Körperhaltungen
        """
        try:
            # Frame in JPEG konvertieren
            _, img_encoded = cv2.imencode(".jpg", frame)

            # API-Anfrage senden
            files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
            response = requests.post(self.analyze_endpoint, files=files)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Fehler bei der Pose Estimation: {response.text}")
                return {"error": response.text}

        except Exception as e:
            logger.error(f"Fehler bei der Pose Estimation: {str(e)}")
            return {"error": str(e)}

    def process_video_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """
        Verarbeitet ein Video-Frame und fügt Metadaten hinzu.

        Args:
            frame: NumPy Array des Bildes
            frame_number: Nummer des Frames

        Returns:
            Dict mit Frame-Metadaten und Pose-Informationen
        """
        pose_data = self.analyze_frame(frame)

        return {
            "frame_number": frame_number,
            "pose_data": pose_data,
            "timestamp": frame_number / 30.0,  # Annahme: 30 FPS
        }

    def get_pose_sequence(self, frames: List[np.ndarray]) -> List[Dict]:
        """
        Verarbeitet eine Sequenz von Frames.

        Args:
            frames: Liste von NumPy Arrays

        Returns:
            Liste von Dictionaries mit Pose-Informationen pro Frame
        """
        results = []
        for i, frame in enumerate(frames):
            result = self.process_video_frame(frame, i)
            results.append(result)
        return results

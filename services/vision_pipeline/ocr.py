# Erweiterung: OCR für Wasserzeichen und Titel
print("Running OCR module...")

import cv2
import numpy as np
import requests
from typing import Dict, List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class OCRDetector:
    def __init__(self, ocr_service_url: str = "http://ocr_detection:8000"):
        self.ocr_service_url = ocr_service_url
        self.analyze_endpoint = f"{ocr_service_url}/analyze"
        self.health_endpoint = f"{ocr_service_url}/health"

    def check_service_health(self) -> bool:
        """Überprüft, ob der OCR Service verfügbar ist."""
        try:
            response = requests.get(self.health_endpoint)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"OCR Service nicht erreichbar: {str(e)}")
            return False

    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analysiert ein einzelnes Frame auf Text.

        Args:
            frame: NumPy Array des Bildes (BGR Format)

        Returns:
            Dict mit den erkannten Texten
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
                logger.error(f"Fehler bei der OCR-Analyse: {response.text}")
                return {"error": response.text}

        except Exception as e:
            logger.error(f"Fehler bei der OCR-Analyse: {str(e)}")
            return {"error": str(e)}

    def process_video_frame(self, frame: np.ndarray, frame_number: int) -> Dict:
        """
        Verarbeitet ein Video-Frame und fügt Metadaten hinzu.

        Args:
            frame: NumPy Array des Bildes
            frame_number: Nummer des Frames

        Returns:
            Dict mit Frame-Metadaten und OCR-Informationen
        """
        start_time = time.time()
        ocr_data = self.analyze_frame(frame)
        processing_time = time.time() - start_time

        return {
            "frame_number": frame_number,
            "ocr_data": ocr_data,
            "processing_time": processing_time,
            "timestamp": frame_number / 30.0,  # Annahme: 30 FPS
        }

    def get_ocr_sequence(self, frames: List[np.ndarray]) -> List[Dict]:
        """
        Verarbeitet eine Sequenz von Frames.

        Args:
            frames: Liste von NumPy Arrays

        Returns:
            Liste von Dictionaries mit OCR-Informationen pro Frame
        """
        results = []
        for i, frame in enumerate(frames):
            result = self.process_video_frame(frame, i)
            results.append(result)
        return results

    def filter_by_confidence(
        self, results: List[Dict], min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        Filtert OCR-Ergebnisse nach Konfidenzwert.

        Args:
            results: Liste von OCR-Ergebnissen
            min_confidence: Minimaler Konfidenzwert

        Returns:
            Gefilterte Liste von Ergebnissen
        """
        filtered_results = []
        for result in results:
            if "ocr_data" in result and "results" in result["ocr_data"]:
                filtered_ocr = [
                    ocr
                    for ocr in result["ocr_data"]["results"]
                    if ocr["confidence"] >= min_confidence
                ]
                if filtered_ocr:
                    result["ocr_data"]["results"] = filtered_ocr
                    filtered_results.append(result)
        return filtered_results

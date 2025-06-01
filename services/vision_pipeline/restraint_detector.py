import asyncio
import hashlib
import io
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
import cv2
import numpy as np
import requests
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("restraint_detector")


class RestraintDetector:
    def __init__(
        self,
        restraint_service_url: str = "http://restraint_detection:8000",
        batch_size: int = 4,
        max_workers: int = 4,
        cache_size: int = 1000,
        frame_sampling_rate: int = 2,
    ) -> None:
        """
        Initialisiert den Restraint-Detektor.

        Args:
            restraint_service_url: URL des Restraint Detection Services
            batch_size: Anzahl der Frames pro Batch
            max_workers: Maximale Anzahl paralleler Worker
            cache_size: Größe des LRU-Caches
            frame_sampling_rate: Jedes n-te Frame wird analysiert
        """
        try:
            self.restraint_service_url = restraint_service_url
            self.analyze_endpoint = f"{restraint_service_url}/analyze"
            self.batch_endpoint = f"{restraint_service_url}/batch_analyze"
            self.health_endpoint = f"{restraint_service_url}/health"

            # Konfiguration
            self.batch_size = batch_size
            self.max_workers = max_workers
            self.frame_sampling_rate = frame_sampling_rate

            # Thread-Pool für parallele Verarbeitung
            self.executor = ThreadPoolExecutor(max_workers=max_workers)

            # Cache für Frame-Hashes
            self._frame_cache = lru_cache(maxsize=cache_size)(
                self._analyze_frame_internal
            )

            # Kategorien für Fesselungen und Materialien
            self.restraint_categories = {
                "rope": ["rope", "cord", "string", "twine"],
                "cuffs": ["handcuffs", "cuffs", "restraints", "shackles"],
                "tape": ["tape", "duct_tape", "adhesive_tape"],
                "chains": ["chains", "metal_chains", "padlocks"],
                "straps": ["straps", "leather_straps", "belts"],
                "gags": ["gags", "mouth_gags", "ball_gags"],
                "blindfolds": ["blindfolds", "eye_covers", "masks"],
            }

            logger.log_info(
                "Restraint-Detector initialisiert",
                extra={
                    "restraint_service_url": restraint_service_url,
                    "batch_size": batch_size,
                    "max_workers": max_workers,
                    "cache_size": cache_size,
                    "frame_sampling_rate": frame_sampling_rate,
                },
            )

        except Exception as e:
            logger.log_error(
                "Fehler bei der Initialisierung des Restraint-Detectors", error=e
            )
            raise

    def _compute_frame_hash(self, frame: np.ndarray) -> str:
        """Berechnet einen Hash für ein Frame zur Caching-Identifikation."""
        try:
            return hashlib.md5(frame.tobytes()).hexdigest()
        except Exception as e:
            logger.log_error("Fehler beim Berechnen des Frame-Hashes", error=e)
            raise

    def _analyze_frame_internal(self, frame: np.ndarray) -> Dict[str, Any]:
        """Interne Methode für die Frame-Analyse mit Caching."""
        try:
            # Frame in JPEG konvertieren
            _, img_encoded = cv2.imencode(".jpg", frame)

            # API-Anfrage senden
            files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
            response = requests.post(self.analyze_endpoint, files=files)

            if response.status_code == 200:
                return response.json()
            else:
                logger.log_error(
                    "Fehler bei der Restraint-Analyse",
                    extra={
                        "status_code": response.status_code,
                        "response_text": response.text,
                    },
                )
                return {"error": response.text}

        except Exception as e:
            logger.log_error("Fehler bei der Restraint-Analyse", error=e)
            return {"error": str(e)}

    async def _process_batch(
        self, session: aiohttp.ClientSession, frames: List[Tuple[np.ndarray, int]]
    ) -> List[Dict[str, Any]]:
        """Verarbeitet einen Batch von Frames asynchron."""
        try:
            # Frames für Batch-Anfrage vorbereiten
            files = []
            for frame, _ in frames:
                _, img_encoded = cv2.imencode(".jpg", frame)
                files.append(
                    ("files", ("frame.jpg", img_encoded.tobytes(), "image/jpeg"))
                )

            # Batch-Anfrage senden
            async with session.post(self.batch_endpoint, data=files) as response:
                if response.status == 200:
                    results = await response.json()
                    return [
                        {
                            "frame_number": frame_number,
                            "restraint_data": result,
                            "processing_time": 0.0,
                            "timestamp": frame_number / 30.0,
                        }
                        for (_, frame_number), result in zip(frames, results)
                    ]
                else:
                    error_text = await response.text()
                    logger.log_error(
                        "Fehler bei der Batch-Analyse",
                        extra={
                            "status_code": response.status,
                            "error_text": error_text,
                        },
                    )
                    return [{"error": "Batch-Analyse fehlgeschlagen"} for _ in frames]

        except Exception as e:
            logger.log_error("Fehler bei der Batch-Verarbeitung", error=e)
            return [{"error": str(e)} for _ in frames]

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Analysiert ein einzelnes Frame auf Fesselungen und Materialien.

        Args:
            frame: NumPy Array des Bildes

        Returns:
            Dict mit den Analyseergebnissen
        """
        try:
            frame_hash = self._compute_frame_hash(frame)
            return self._frame_cache(frame_hash)
        except Exception as e:
            logger.log_error("Fehler bei der Frame-Analyse", error=e)
            return {"error": str(e)}

    async def process_video_sequence(
        self, frames: List[np.ndarray], frame_numbers: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Verarbeitet eine Sequenz von Frames effizient.

        Args:
            frames: Liste von Frames
            frame_numbers: Liste von Frame-Nummern

        Returns:
            Liste von Analyseergebnissen
        """
        try:
            logger.log_info(
                "Starte Verarbeitung der Video-Sequenz",
                extra={"frame_count": len(frames), "batch_size": self.batch_size},
            )

            # Frames in Batches aufteilen
            batches = []
            current_batch = []

            for frame, frame_number in zip(frames, frame_numbers):
                # Frame-Hashing für Caching
                frame_hash = self._compute_frame_hash(frame)

                # Prüfen ob Frame bereits im Cache
                if frame_hash in self._frame_cache.cache_info():
                    continue

                current_batch.append((frame, frame_number))

                if len(current_batch) >= self.batch_size:
                    batches.append(current_batch)
                    current_batch = []

            if current_batch:
                batches.append(current_batch)

            # Asynchrone Batch-Verarbeitung
            async with aiohttp.ClientSession() as session:
                tasks = [self._process_batch(session, batch) for batch in batches]
                results = await asyncio.gather(*tasks)

            # Ergebnisse zusammenführen
            final_results = [item for sublist in results for item in sublist]

            logger.log_info(
                "Video-Sequenz erfolgreich verarbeitet",
                extra={
                    "processed_frames": len(final_results),
                    "cache_hits": len(frames) - len(final_results),
                },
            )

            return final_results

        except Exception as e:
            logger.log_error("Fehler bei der Verarbeitung der Video-Sequenz", error=e)
            raise

    def process_video_frame(
        self, frame: np.ndarray, frame_number: int
    ) -> Dict[str, Any]:
        """
        Verarbeitet ein einzelnes Video-Frame.

        Args:
            frame: NumPy Array des Bildes
            frame_number: Nummer des Frames

        Returns:
            Dict mit Frame-Metadaten und Analyse-Informationen
        """
        try:
            # Frame-Sampling: Nur jedes n-te Frame analysieren
            if frame_number % self.frame_sampling_rate != 0:
                return {
                    "frame_number": frame_number,
                    "restraint_data": {"skipped": True},
                    "processing_time": 0.0,
                    "timestamp": frame_number / 30.0,
                }

            start_time = time.time()
            restraint_data = self.analyze_frame(frame)
            processing_time = time.time() - start_time

            return {
                "frame_number": frame_number,
                "restraint_data": restraint_data,
                "processing_time": processing_time,
                "timestamp": frame_number / 30.0,
            }

        except Exception as e:
            logger.log_error(
                "Fehler bei der Verarbeitung des Video-Frames",
                error=e,
                extra={"frame_number": frame_number},
            )
            return {
                "frame_number": frame_number,
                "error": str(e),
                "processing_time": 0.0,
                "timestamp": frame_number / 30.0,
            }

    def filter_by_confidence(
        self, results: List[Dict[str, Any]], min_confidence: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Filtert Ergebnisse nach Konfidenzwert.

        Args:
            results: Liste von Analyseergebnissen
            min_confidence: Minimaler Konfidenzwert

        Returns:
            Gefilterte Liste von Ergebnissen
        """
        try:
            filtered_results = []
            for result in results:
                if "restraint_data" in result and "results" in result["restraint_data"]:
                    filtered_data = [
                        item
                        for item in result["restraint_data"]["results"]
                        if item["confidence"] >= min_confidence
                    ]
                    if filtered_data:
                        result["restraint_data"]["results"] = filtered_data
                        filtered_results.append(result)

            logger.log_info(
                "Restraint-Ergebnisse gefiltert",
                extra={
                    "total_results": len(results),
                    "filtered_results": len(filtered_results),
                    "min_confidence": min_confidence,
                },
            )

            return filtered_results

        except Exception as e:
            logger.log_error("Fehler beim Filtern der Restraint-Ergebnisse", error=e)
            raise

    def check_service_health(self) -> bool:
        """Überprüft, ob der Restraint Detection Service verfügbar ist."""
        try:
            response = requests.get(self.health_endpoint)
            return response.status_code == 200
        except Exception as e:
            logger.log_error("Restraint Detection Service nicht erreichbar", error=e)
            return False

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BatchProcessor:
    def __init__(self):
        self.batch_id = os.getenv("BATCH_ID")
        if not self.batch_id:
            raise ValueError("BATCH_ID nicht gesetzt")

        self.api_url = os.getenv("API_URL", "http://api:8000")
        self.working_dir = "/app/data"
        self.batch_dir = f"{self.working_dir}/jobs/{self.batch_id}"

    async def start(self):
        """Startet die Batch-Verarbeitung"""
        try:
            logger.info(f"Starte Verarbeitung von Batch {self.batch_id}")

            # Batch-Metadaten laden
            batch = self._load_batch_metadata()
            if not batch:
                raise Exception("Batch-Metadaten nicht gefunden")

            # Verarbeitungsstatus aktualisieren
            await self._update_batch_status("processing")

            # Jobs verarbeiten
            for job in batch["jobs"]:
                await self._process_job(job)

            # Batch abschließen
            await self._update_batch_status("completed")
            logger.info(f"Batch {self.batch_id} erfolgreich abgeschlossen")

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {str(e)}")
            await self._update_batch_status("error", str(e))
            sys.exit(1)

    def _load_batch_metadata(self) -> Optional[Dict]:
        """Lädt die Batch-Metadaten"""
        try:
            metadata_path = f"{self.batch_dir}/metadata.json"
            if not os.path.exists(metadata_path):
                return None

            with open(metadata_path, "r") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Fehler beim Laden der Batch-Metadaten: {str(e)}")
            return None

    async def _update_batch_status(
        self, status: str, error_message: Optional[str] = None
    ):
        """Aktualisiert den Batch-Status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/batches/{self.batch_id}/status",
                    json={"status": status, "error": error_message},
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Aktualisieren des Batch-Status: {await response.text()}"
                        )

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Batch-Status: {str(e)}")

    async def _process_job(self, job: Dict):
        """Verarbeitet einen einzelnen Job"""
        try:
            job_id = job["id"]
            job_type = job["type"]

            logger.info(f"Verarbeite Job {job_id} (Typ: {job_type})")

            # Job-Status aktualisieren
            await self._update_job_status(job_id, "processing")

            # Job-spezifische Verarbeitung
            if job_type == "video":
                await self._process_video_job(job)
            elif job_type == "image":
                await self._process_image_job(job)
            else:
                raise Exception(f"Unbekannter Job-Typ: {job_type}")

            # Job abschließen
            await self._update_job_status(job_id, "completed")
            logger.info(f"Job {job_id} erfolgreich abgeschlossen")

        except Exception as e:
            logger.error(f"Fehler bei der Job-Verarbeitung: {str(e)}")
            await self._update_job_status(job_id, "error", str(e))
            raise

    async def _update_job_status(
        self, job_id: str, status: str, error_message: Optional[str] = None
    ):
        """Aktualisiert den Job-Status"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/jobs/{job_id}/status",
                    json={"status": status, "error": error_message},
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Aktualisieren des Job-Status: {await response.text()}"
                        )

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Job-Status: {str(e)}")

    async def _process_video_job(self, job: Dict):
        """Verarbeitet einen Video-Job"""
        try:
            job_id = job["id"]
            input_path = f"{self.working_dir}/incoming/videos/{job_id}/raw"
            output_path = f"{self.working_dir}/jobs/{self.batch_id}/results/{job_id}"

            # Ausgabeverzeichnis erstellen
            os.makedirs(output_path, exist_ok=True)

            # Video-Verarbeitungspipeline ausführen
            # TODO: Implementiere die tatsächliche Video-Verarbeitung
            # Beispiel:
            # 1. Video in Frames extrahieren
            # 2. Frames analysieren
            # 3. Ergebnisse speichern

            # Temporäre Dateien bereinigen
            self._cleanup_temp_files(input_path)

        except Exception as e:
            logger.error(f"Fehler bei der Video-Verarbeitung: {str(e)}")
            raise

    async def _process_image_job(self, job: Dict):
        """Verarbeitet einen Bild-Job"""
        try:
            job_id = job["id"]
            input_path = f"{self.working_dir}/incoming/images/{job_id}/raw"
            output_path = f"{self.working_dir}/jobs/{self.batch_id}/results/{job_id}"

            # Ausgabeverzeichnis erstellen
            os.makedirs(output_path, exist_ok=True)

            # Bild-Verarbeitungspipeline ausführen
            # TODO: Implementiere die tatsächliche Bild-Verarbeitung
            # Beispiel:
            # 1. Bilder analysieren
            # 2. Ergebnisse speichern

            # Temporäre Dateien bereinigen
            self._cleanup_temp_files(input_path)

        except Exception as e:
            logger.error(f"Fehler bei der Bild-Verarbeitung: {str(e)}")
            raise

    def _cleanup_temp_files(self, directory: str):
        """Bereinigt temporäre Dateien"""
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(".tmp"):
                        os.remove(os.path.join(root, file))
        except Exception as e:
            logger.error(f"Fehler beim Bereinigen temporärer Dateien: {str(e)}")


if __name__ == "__main__":
    processor = BatchProcessor()
    asyncio.run(processor.start())

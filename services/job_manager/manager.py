import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Optional

import redis
from gpu_providers import RunPodProvider, VastAIProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GPUInstance:
    id: str
    provider: str  # 'vast' oder 'runpod'
    cost_per_hour: float
    created_at: datetime
    status: str
    batch_id: Optional[str]


class JobManager:
    def __init__(self):
        self.redis_client = redis.Redis(host="redis", port=6379, db=0)
        self.batch_threshold_hours = int(os.getenv("BATCH_THRESHOLD_HOURS", 4))
        self.min_jobs_per_batch = int(os.getenv("MIN_JOBS_PER_BATCH", 3))
        self.auto_process_jobs = (
            os.getenv("AUTO_PROCESS_JOBS", "false").lower() == "true"
        )
        self.active_instances: Dict[str, GPUInstance] = {}
        self.batch_cache = {}
        self.job_cache = {}

        # GPU-Provider initialisieren
        self.vast_provider = VastAIProvider()
        self.runpod_provider = RunPodProvider()

    @lru_cache(maxsize=1000)
    def get_cached_job(self, job_id: str) -> Optional[Dict]:
        """Cache für Job-Metadaten"""
        return self.job_cache.get(job_id)

    @lru_cache(maxsize=100)
    def get_cached_batch(self, batch_id: str) -> Optional[Dict]:
        """Cache für Batch-Metadaten"""
        return self.batch_cache.get(batch_id)

    async def start(self):
        """Startet den Job-Manager mit optimierter Batch-Verarbeitung"""
        logger.info("Job-Manager gestartet")
        logger.info(
            f"Automatische Job-Verarbeitung: {'aktiviert' if self.auto_process_jobs else 'deaktiviert'}"
        )

        # Cache initialisieren
        await self._initialize_caches()

        while True:
            try:
                if self.auto_process_jobs:
                    await self.process_pending_jobs()
                await self.cleanup_completed_batches()
                await self.check_gpu_instances()
                await asyncio.sleep(30)  # Reduzierte Prüfintervall
            except Exception as e:
                logger.error(f"Fehler im Job-Manager: {str(e)}")
                await asyncio.sleep(30)

    async def _initialize_caches(self):
        """Initialisiert die Caches mit vorhandenen Jobs und Batches."""
        try:
            # Phase 1: Job-Cache initialisieren
            await self._load_job_cache()

            # Phase 2: Batch-Cache initialisieren
            await self._load_batch_cache()

            # Phase 3: Cache-Statistiken loggen
            self._log_cache_initialization()

        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Caches: {str(e)}")

    async def _load_job_cache(self) -> None:
        """Lädt Job-Metadaten in den Cache."""
        jobs_path = "data/jobs"

        if not os.path.exists(jobs_path):
            return

        for job_id in os.listdir(jobs_path):
            try:
                await self._load_single_job(jobs_path, job_id)
            except Exception as e:
                logger.warning(f"Fehler beim Laden von Job {job_id}: {str(e)}")

    async def _load_batch_cache(self) -> None:
        """Lädt Batch-Metadaten in den Cache."""
        batches_path = "data/batches"

        if not os.path.exists(batches_path):
            return

        for batch_id in os.listdir(batches_path):
            try:
                await self._load_single_batch(batches_path, batch_id)
            except Exception as e:
                logger.warning(f"Fehler beim Laden von Batch {batch_id}: {str(e)}")

    async def _load_single_job(self, jobs_path: str, job_id: str) -> None:
        """Lädt einen einzelnen Job in den Cache."""
        job_path = os.path.join(jobs_path, job_id)

        if not os.path.isdir(job_path):
            return

        metadata_path = os.path.join(job_path, "metadata.json")

        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                job = json.load(f)
                self.job_cache[job_id] = job

    async def _load_single_batch(self, batches_path: str, batch_id: str) -> None:
        """Lädt einen einzelnen Batch in den Cache."""
        batch_path = os.path.join(batches_path, batch_id)

        if not os.path.isdir(batch_path):
            return

        metadata_path = os.path.join(batch_path, "metadata.json")

        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                batch = json.load(f)
                self.batch_cache[batch_id] = batch

    def _log_cache_initialization(self) -> None:
        """Loggt Cache-Initialisierungs-Statistiken."""
        logger.info(f"Cache initialisiert: {len(self.job_cache)} Jobs, {len(self.batch_cache)} Batches")

    async def process_pending_jobs(self):
        """Optimierte Verarbeitung wartender Jobs mit Batch-Processing"""
        try:
            pending_jobs = self.get_pending_jobs()
            if not pending_jobs:
                return

            # Jobs nach Typ und Priorität gruppieren
            job_groups = self._group_jobs_by_type_and_priority(pending_jobs)

            for group, jobs in job_groups.items():
                if len(jobs) >= self.min_jobs_per_batch:
                    await self.create_batches(jobs)
                elif jobs and self._should_create_small_batch(jobs):
                    await self.create_batches(jobs)

        except Exception as e:
            logger.error(f"Fehler bei der Job-Verarbeitung: {str(e)}")

    def _group_jobs_by_type_and_priority(
        self, jobs: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Gruppiert Jobs nach Typ und Priorität für optimierte Batch-Verarbeitung"""
        groups = {}
        for job in jobs:
            key = f"{job['type']}_{job.get('priority', 'normal')}"
            if key not in groups:
                groups[key] = []
            groups[key].append(job)
        return groups

    async def start_batch_processing(self, batch_id: str):
        """Startet die Verarbeitung eines Batches manuell"""
        try:
            # Batch-Metadaten laden
            batch_path = f"data/jobs/{batch_id}"
            metadata_path = f"{batch_path}/metadata.json"

            if not os.path.exists(metadata_path):
                raise Exception(f"Batch {batch_id} nicht gefunden")

            with open(metadata_path, "r") as f:
                batch = json.load(f)

            if batch["status"] != "pending":
                raise Exception(f"Batch {batch_id} ist nicht im Status 'pending'")

            # GPU-Instanz erstellen
            await self.create_gpu_instance(batch_id)

            logger.info(f"Manuelle Verarbeitung von Batch {batch_id} gestartet")

        except Exception as e:
            logger.error(f"Fehler beim Starten der Batch-Verarbeitung: {str(e)}")
            raise

    async def create_batch(self, job_ids: List[str], batch_name: Optional[str] = None):
        """Erstellt einen neuen Batch manuell"""
        try:
            # Jobs laden und validieren
            jobs = []
            for job_id in job_ids:
                job_path = self.find_job_path(job_id)
                if not job_path:
                    raise Exception(f"Job {job_id} nicht gefunden")

                metadata_path = f"{job_path}/metadata.json"
                with open(metadata_path, "r") as f:
                    job = json.load(f)
                    if job["status"] != "pending":
                        raise Exception(f"Job {job_id} ist nicht im Status 'pending'")
                    jobs.append(job)

            if not jobs:
                raise Exception("Keine gültigen Jobs gefunden")

            # Batch erstellen
            batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if batch_name:
                batch_id = f"{batch_id}_{batch_name}"

            await self.save_batch(jobs, batch_id)

            logger.info(f"Batch {batch_id} mit {len(jobs)} Jobs erstellt")
            return batch_id

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Batches: {str(e)}")
            raise

    async def save_batch(self, jobs: List[Dict], batch_id: Optional[str] = None):
        """Speichert einen Batch"""
        try:
            if not batch_id:
                batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            batch_path = f"data/jobs/{batch_id}"
            os.makedirs(batch_path, exist_ok=True)

            # Batch-Metadaten erstellen
            batch = {
                "id": batch_id,
                "jobs": jobs,
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                "estimated_duration": sum(self.estimate_job_duration(j) for j in jobs),
                "created_by": "operator" if not self.auto_process_jobs else "system",
            }

            # Batch speichern
            with open(f"{batch_path}/metadata.json", "w") as f:
                json.dump(batch, f, default=str)

            # Jobs aktualisieren
            for job in jobs:
                job["batch_id"] = batch_id
                job["status"] = "batched"
                job_path = self.find_job_path(job["id"])
                with open(f"{job_path}/metadata.json", "w") as f:
                    json.dump(job, f, default=str)

            # GPU-Instanz erstellen, wenn automatische Verarbeitung aktiviert ist
            if self.auto_process_jobs:
                await self.create_gpu_instance(batch_id)

        except Exception as e:
            logger.error(f"Fehler beim Speichern des Batches: {str(e)}")
            raise

    def _should_create_small_batch(self, jobs: List[Dict]) -> bool:
        """Entscheidet, ob ein kleiner Batch erstellt werden soll"""
        # Berechne die geschätzte Gesamtdauer
        total_duration = sum(self.estimate_job_duration(job) for job in jobs)

        # Erstelle einen kleinen Batch, wenn:
        # 1. Die Gesamtdauer einen Mindestwert überschreitet
        # 2. Die Jobs seit einer bestimmten Zeit warten
        min_duration = 0.5  # Mindestens 30 Minuten
        max_wait_time = 2.0  # Maximal 2 Stunden warten

        if total_duration >= min_duration:
            return True

        # Prüfe Wartezeit des ältesten Jobs
        oldest_job = min(jobs, key=lambda j: datetime.fromisoformat(j["created_at"]))
        wait_time = (
            datetime.now() - datetime.fromisoformat(oldest_job["created_at"])
        ).total_seconds() / 3600

        return wait_time >= max_wait_time

    async def create_batches(self, jobs: List[Dict]):
        """Erstellt Batches aus Jobs"""
        if not jobs:
            return

        # Jobs nach Größe und Typ gruppieren
        current_batch = []
        current_duration = 0
        batch_count = 0

        for job in jobs:
            job_duration = self.estimate_job_duration(job)

            # Prüfe, ob Job zum aktuellen Batch passt
            if (
                current_duration + job_duration <= self.batch_threshold_hours
                and len(current_batch) < self.min_jobs_per_batch
            ):
                current_batch.append(job)
                current_duration += job_duration
            else:
                # Aktuellen Batch speichern und neuen starten
                if current_batch:
                    await self.save_batch(current_batch)
                    batch_count += 1
                current_batch = [job]
                current_duration = job_duration

        # Letzten Batch speichern
        if current_batch:
            await self.save_batch(current_batch)
            batch_count += 1

        logger.info(f"{batch_count} Batches erstellt")

    async def check_gpu_instances(self):
        """Überprüft den Status aller GPU-Instanzen"""
        try:
            for instance_id, instance in list(self.active_instances.items()):
                # Gesundheitscheck durchführen
                if instance.provider == "vast":
                    is_healthy = await self.vast_provider.check_instance_health(
                        instance
                    )
                else:
                    is_healthy = await self.runpod_provider.check_instance_health(
                        instance
                    )

                # Wenn Instanz nicht gesund ist, behandeln
                if not is_healthy:
                    await self._handle_unusable_instance(
                        instance_id, instance, instance.status.value
                    )

        except Exception as e:
            logger.error(f"Fehler beim Überprüfen der GPU-Instanzen: {str(e)}")

    async def _handle_unusable_instance(
        self, instance_id: str, instance: GPUInstance, status: str
    ):
        """Behandelt nicht nutzbare GPU-Instanzen"""
        try:
            # Batch-Status aktualisieren
            if instance.batch_id:
                self._update_batch_status(
                    instance.batch_id, "error", f"GPU-Instanz nicht nutzbar: {status}"
                )

            # GPU-Instanz löschen
            await self.delete_gpu_instance(instance_id)

            # Aus aktiven Instanzen entfernen
            del self.active_instances[instance_id]

            logger.warning(
                f"GPU-Instanz {instance_id} wurde gelöscht (Status: {status})"
            )

        except Exception as e:
            logger.error(
                f"Fehler beim Behandeln der nicht nutzbaren GPU-Instanz: {str(e)}"
            )

    async def create_gpu_instance(self, batch_id: str):
        """Erstellt eine GPU-Instanz für einen Batch"""
        try:
            # Provider auswählen (hier: Vast.ai als Standard)
            provider = self.vast_provider

            # Instanz erstellen
            instance = await provider.create_instance(batch_id)

            # Warte auf Verfügbarkeit der Instanz
            max_retries = 5
            retry_delay = 30  # Sekunden

            for _ in range(max_retries):
                status = await provider.get_instance_status(instance.id)
                if status == "running":
                    break
                elif status in ["error", "stopped", "unreachable"]:
                    await self._handle_unusable_instance(instance.id, instance, status)
                    raise Exception(
                        f"GPU-Instanz konnte nicht gestartet werden: {status}"
                    )
                await asyncio.sleep(retry_delay)
            else:
                await self._handle_unusable_instance(instance.id, instance, "timeout")
                raise Exception("Timeout beim Warten auf GPU-Instanz")

            # Instanz speichern
            self.active_instances[instance.id] = instance

            # Batch aktualisieren
            batch_path = f"data/jobs/{batch_id}"
            metadata_path = f"{batch_path}/metadata.json"

            with open(metadata_path, "r") as f:
                batch = json.load(f)

            batch["gpu_instance_id"] = instance.id
            batch["gpu_provider"] = instance.provider

            with open(metadata_path, "w") as f:
                json.dump(batch, f, default=str)

            logger.info(f"GPU-Instanz {instance.id} für Batch {batch_id} erstellt")

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der GPU-Instanz: {str(e)}")
            # Batch-Status auf Fehler setzen
            self._update_batch_status(batch_id, "error", str(e))

    async def delete_gpu_instance(self, instance_id: str):
        """Löscht eine GPU-Instanz"""
        try:
            instance = self.active_instances.get(instance_id)
            if not instance:
                logger.warning(f"GPU-Instanz {instance_id} nicht gefunden")
                return

            # Instanz löschen
            if instance.provider == "vast":
                await self.vast_provider.delete_instance(instance_id)
            else:
                await self.runpod_provider.delete_instance(instance_id)

            # Aus aktiven Instanzen entfernen
            del self.active_instances[instance_id]

            logger.info(f"GPU-Instanz {instance_id} gelöscht")

        except Exception as e:
            logger.error(f"Fehler beim Löschen der GPU-Instanz: {str(e)}")

    async def cleanup_completed_batches(self):
        """Bereinigt abgeschlossene Batches und GPU-Instanzen"""
        try:
            batch_path = "data/jobs"
            if not os.path.exists(batch_path):
                return

            for batch_id in os.listdir(batch_path):
                metadata_path = f"{batch_path}/{batch_id}/metadata.json"
                if not os.path.exists(metadata_path):
                    continue

                with open(metadata_path, "r") as f:
                    batch = json.load(f)

                # Prüfe, ob Batch abgeschlossen ist
                if batch["status"] == "completed":
                    # GPU-Instanz löschen
                    if batch.get("gpu_instance_id"):
                        await self.delete_gpu_instance(batch["gpu_instance_id"])

                        # Batch-Verzeichnis bereinigen
                        self._cleanup_batch_directory(batch_id)

                        logger.info(f"Batch {batch_id} bereinigt")

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Bereinigung: {str(e)}")

    def _cleanup_batch_directory(self, batch_id: str):
        """Bereinigt das Batch-Verzeichnis"""
        try:
            batch_path = f"data/jobs/{batch_id}"
            if os.path.exists(batch_path):
                # Temporäre Dateien löschen
                for root, dirs, files in os.walk(batch_path):
                    for file in files:
                        if file.endswith(".tmp"):
                            os.remove(os.path.join(root, file))

                # Verzeichnis löschen, wenn leer
                if not os.listdir(batch_path):
                    os.rmdir(batch_path)

        except Exception as e:
            logger.error(f"Fehler beim Bereinigen des Batch-Verzeichnisses: {str(e)}")

    def _update_batch_status(
        self, batch_id: str, status: str, error_message: Optional[str] = None
    ):
        """Aktualisiert den Status eines Batches"""
        try:
            batch_path = f"data/jobs/{batch_id}"
            metadata_path = f"{batch_path}/metadata.json"

            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    batch = json.load(f)

                batch["status"] = status
                if error_message:
                    batch["error"] = error_message

                with open(metadata_path, "w") as f:
                    json.dump(batch, f, default=str)

        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren des Batch-Status: {str(e)}")

    def get_pending_jobs(self) -> List[Dict]:
        """Lädt wartende Jobs"""
        jobs = []
        base_path = "data/incoming"

        for media_type in ["videos", "images"]:
            media_path = f"{base_path}/{media_type}"
            if not os.path.exists(media_path):
                continue

            for job_id in os.listdir(media_path):
                metadata_path = f"{media_path}/{job_id}/metadata.json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        job_data = json.load(f)
                        if job_data["status"] == "pending":
                            jobs.append(job_data)

        return jobs

    def estimate_job_duration(self, job: Dict) -> float:
        """Schätzt die Verarbeitungsdauer eines Jobs"""
        # Basis-Schätzung nach Job-Typ
        base_duration = 1.0 if job["type"] == "video" else 0.1

        # Berücksichtige Dateigröße
        file_size = job.get("file_size", 0)  # in Bytes
        if file_size > 0:
            # Video: 1 Stunde pro GB
            # Bild: 0.1 Stunden pro MB
            if job["type"] == "video":
                base_duration += file_size / (1024 * 1024 * 1024)  # GB
            else:
                base_duration += file_size / (1024 * 1024) * 0.1  # MB

        return base_duration

    def find_job_path(self, job_id: str) -> Optional[str]:
        """Findet den Pfad zu einem Job"""
        for media_type in ["videos", "images"]:
            path = f"data/incoming/{media_type}/{job_id}"
            if os.path.exists(path):
                return path
        return None


if __name__ == "__main__":
    manager = JobManager()
    asyncio.run(manager.start())

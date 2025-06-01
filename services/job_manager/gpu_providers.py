from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List
import aiohttp
import os
import json
import logging
import asyncio
from enum import Enum
import asyncssh
import re

logger = logging.getLogger(__name__)


class GPUStatus(Enum):
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"
    UNREACHABLE = "unreachable"
    UNKNOWN = "unknown"


@dataclass
class GPUHealth:
    gpu_utilization: float
    memory_utilization: float
    temperature: float
    power_usage: float
    is_healthy: bool
    error_message: Optional[str] = None


@dataclass
class GPUInstance:
    id: str
    provider: str
    cost_per_hour: float
    created_at: datetime
    status: GPUStatus
    batch_id: Optional[str]
    ssh_host: str
    ssh_port: int
    ssh_user: str
    ssh_key: str
    last_status_check: datetime
    consecutive_failures: int = 0
    last_health_check: Optional[GPUHealth] = None


class GPUProvider(ABC):
    @abstractmethod
    async def create_instance(self, batch_id: str) -> GPUInstance:
        """Erstellt eine neue GPU-Instanz"""
        pass

    @abstractmethod
    async def delete_instance(self, instance_id: str):
        """Löscht eine GPU-Instanz"""
        pass

    @abstractmethod
    async def get_instance_status(self, instance_id: str) -> GPUStatus:
        """Gibt den Status einer GPU-Instanz zurück"""
        pass

    @abstractmethod
    async def check_instance_health(self, instance: GPUInstance) -> bool:
        """Überprüft die Gesundheit einer GPU-Instanz"""
        pass


class VastAIProvider(GPUProvider):
    def __init__(self):
        self.api_key = os.getenv("VAST_API_KEY")
        if not self.api_key:
            raise ValueError("VAST_API_KEY nicht gefunden")

        self.api_url = "https://vast.ai/api/v0"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.max_consecutive_failures = 3
        self.health_check_timeout = 30  # Sekunden

    async def create_instance(self, batch_id: str) -> GPUInstance:
        try:
            # Angebote suchen
            offers = await self._search_offers()
            if not offers:
                raise Exception("Keine GPU-Angebote verfügbar")

            # Bestes Angebot auswählen
            best_offer = self._select_best_offer(offers)

            # Instanz erstellen
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/asks/create/",
                    headers=self.headers,
                    json={
                        "client_id": best_offer["client_id"],
                        "price": best_offer["price"],
                        "image": "nvidia/cuda:11.8.0-base-ubuntu22.04",
                        "onstart": self._get_startup_script(),
                    },
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Erstellen der Instanz: {await response.text()}"
                        )

                    data = await response.json()
                    return self._create_instance_from_response(data, batch_id)

        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Vast.ai Instanz: {str(e)}")
            raise

    async def delete_instance(self, instance_id: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/instances/{instance_id}/destroy/",
                    headers=self.headers,
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Löschen der Instanz: {await response.text()}"
                        )

        except Exception as e:
            logger.error(f"Fehler beim Löschen der Vast.ai Instanz: {str(e)}")
            raise

    async def get_instance_status(self, instance_id: str) -> GPUStatus:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/instances/{instance_id}/", headers=self.headers
                ) as response:
                    if response.status != 200:
                        return GPUStatus.UNREACHABLE

                    data = await response.json()
                    return self._map_vast_status(data["status"])

        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Vast.ai Instanz-Status: {str(e)}")
            return GPUStatus.UNREACHABLE

    async def check_instance_health(self, instance: GPUInstance) -> bool:
        """Überprüft die Gesundheit einer GPU-Instanz"""
        try:
            # Status abrufen
            status = await self.get_instance_status(instance.id)

            # Status aktualisieren
            instance.status = status
            instance.last_status_check = datetime.now()

            # Prüfe auf Probleme
            if status in [GPUStatus.ERROR, GPUStatus.UNREACHABLE, GPUStatus.STOPPED]:
                instance.consecutive_failures += 1
                if instance.consecutive_failures >= self.max_consecutive_failures:
                    logger.warning(
                        f"GPU-Instanz {instance.id} hat zu viele aufeinanderfolgende Fehler"
                    )
                    return False
            else:
                instance.consecutive_failures = 0

            # SSH-Verbindung testen und GPU-Status prüfen
            if status == GPUStatus.RUNNING:
                try:
                    async with asyncio.timeout(self.health_check_timeout):
                        health = await self._check_gpu_health(instance)
                        instance.last_health_check = health

                        if not health.is_healthy:
                            logger.warning(
                                f"GPU-Instanz {instance.id} ist nicht gesund: "
                                f"GPU: {health.gpu_utilization}%, "
                                f"Memory: {health.memory_utilization}%, "
                                f"Temp: {health.temperature}°C, "
                                f"Power: {health.power_usage}W"
                            )
                            return False

                except asyncio.TimeoutError:
                    logger.warning(
                        f"Timeout beim Gesundheitscheck für GPU-Instanz {instance.id}"
                    )
                    return False
                except Exception as e:
                    logger.error(f"Fehler beim GPU-Gesundheitscheck: {str(e)}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Fehler beim Gesundheitscheck der GPU-Instanz: {str(e)}")
            return False

    async def _check_gpu_health(self, instance: GPUInstance) -> GPUHealth:
        """Führt einen detaillierten GPU-Gesundheitscheck durch"""
        try:
            # SSH-Verbindung herstellen
            async with asyncssh.connect(
                instance.ssh_host,
                port=instance.ssh_port,
                username=instance.ssh_user,
                client_keys=[instance.ssh_key],
                known_hosts=None,
            ) as conn:
                # GPU-Status abrufen
                result = await conn.run(
                    "nvidia-smi --query-gpu=utilization.gpu,utilization.memory,temperature.gpu,power.draw --format=csv,noheader,nounits"
                )

                if result.exit_status != 0:
                    return GPUHealth(
                        gpu_utilization=0,
                        memory_utilization=0,
                        temperature=0,
                        power_usage=0,
                        is_healthy=False,
                        error_message=f"nvidia-smi Fehler: {result.stderr}",
                    )

                # Werte parsen
                values = result.stdout.strip().split(",")
                if len(values) != 4:
                    return GPUHealth(
                        gpu_utilization=0,
                        memory_utilization=0,
                        temperature=0,
                        power_usage=0,
                        is_healthy=False,
                        error_message="Ungültiges nvidia-smi Format",
                    )

                try:
                    gpu_util = float(values[0])
                    mem_util = float(values[1])
                    temp = float(values[2])
                    power = float(values[3])
                except ValueError:
                    return GPUHealth(
                        gpu_utilization=0,
                        memory_utilization=0,
                        temperature=0,
                        power_usage=0,
                        is_healthy=False,
                        error_message="Ungültige GPU-Werte",
                    )

                # Gesundheitskriterien prüfen
                is_healthy = (
                    gpu_util >= 0
                    and gpu_util <= 100
                    and mem_util >= 0
                    and mem_util <= 100
                    and temp >= 0
                    and temp <= 85
                    and power >= 0
                    and power <= 300
                )

                return GPUHealth(
                    gpu_utilization=gpu_util,
                    memory_utilization=mem_util,
                    temperature=temp,
                    power_usage=power,
                    is_healthy=is_healthy,
                )

        except Exception as e:
            return GPUHealth(
                gpu_utilization=0,
                memory_utilization=0,
                temperature=0,
                power_usage=0,
                is_healthy=False,
                error_message=str(e),
            )

    def _map_vast_status(self, vast_status: str) -> GPUStatus:
        """Mappt Vast.ai Status auf GPUStatus Enum"""
        status_map = {
            "creating": GPUStatus.CREATING,
            "running": GPUStatus.RUNNING,
            "stopped": GPUStatus.STOPPED,
            "error": GPUStatus.ERROR,
            "destroyed": GPUStatus.DESTROYED,
        }
        return status_map.get(vast_status, GPUStatus.UNKNOWN)

    async def _search_offers(self) -> List[Dict]:
        """Sucht nach verfügbaren GPU-Angeboten"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/bundles/",
                    headers=self.headers,
                    params={"q": "reliability > 0.95 num_gpus=1", "order_by": "score-"},
                ) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Suchen nach Angeboten: {await response.text()}"
                        )

                    return await response.json()

        except Exception as e:
            logger.error(f"Fehler beim Suchen nach Vast.ai Angeboten: {str(e)}")
            raise

    def _select_best_offer(self, offers: List[Dict]) -> Dict:
        """Wählt das beste Angebot aus"""
        if not offers:
            raise Exception("Keine Angebote verfügbar")

        # Sortiere nach Preis und Zuverlässigkeit
        sorted_offers = sorted(offers, key=lambda x: (x["price"], -x["reliability"]))

        return sorted_offers[0]

    def _get_startup_script(self) -> str:
        """Gibt das Startup-Skript für die Instanz zurück"""
        return """
        #!/bin/bash
        apt-get update
        apt-get install -y python3-pip
        pip3 install -r /app/requirements.txt
        python3 /app/process_batch.py
        """

    def _create_instance_from_response(self, data: Dict, batch_id: str) -> GPUInstance:
        """Erstellt ein GPUInstance-Objekt aus der API-Antwort"""
        return GPUInstance(
            id=data["id"],
            provider="vast",
            cost_per_hour=float(data["price"]),
            created_at=datetime.now(),
            status=GPUStatus.CREATING,
            batch_id=batch_id,
            ssh_host=data["ssh_host"],
            ssh_port=data["ssh_port"],
            ssh_user=data["ssh_user"],
            ssh_key=data["ssh_key"],
            last_status_check=datetime.now(),
            consecutive_failures=0,
        )


class RunPodProvider(GPUProvider):
    def __init__(self):
        self.api_key = os.getenv("RUNPOD_API_KEY")
        if not self.api_key:
            raise ValueError("RUNPOD_API_KEY nicht gefunden")

        self.api_url = "https://api.runpod.io/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.max_consecutive_failures = 3
        self.health_check_timeout = 30  # Sekunden

    async def create_instance(self, batch_id: str) -> GPUInstance:
        try:
            # TODO: Implementiere RunPod-Instanzerstellung
            raise NotImplementedError("RunPod-Provider noch nicht implementiert")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der RunPod Instanz: {str(e)}")
            raise

    async def delete_instance(self, instance_id: str):
        try:
            # TODO: Implementiere RunPod-Instanzlöschung
            raise NotImplementedError("RunPod-Provider noch nicht implementiert")
        except Exception as e:
            logger.error(f"Fehler beim Löschen der RunPod Instanz: {str(e)}")
            raise

    async def get_instance_status(self, instance_id: str) -> GPUStatus:
        try:
            # TODO: Implementiere RunPod-Statusabruf
            raise NotImplementedError("RunPod-Provider noch nicht implementiert")
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des RunPod Instanz-Status: {str(e)}")
            raise

    async def check_instance_health(self, instance: GPUInstance) -> bool:
        try:
            # TODO: Implementiere RunPod-Gesundheitscheck
            raise NotImplementedError("RunPod-Provider noch nicht implementiert")
        except Exception as e:
            logger.error(f"Fehler beim Gesundheitscheck der RunPod Instanz: {str(e)}")
            raise

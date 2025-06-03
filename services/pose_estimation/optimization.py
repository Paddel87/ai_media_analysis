import asyncio
import json
import logging
import os
from typing import Any, Dict

import psutil
import redis.asyncio as redis
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    memory_threshold: float = 0.8
    gc_threshold: float = 0.9
    base_concurrency_limit: int = 4
    max_concurrency_limit: int = 8
    min_concurrency_limit: int = 2
    cache_ttl: int = 3600
    cache_max_size: int = 1000
    alert_threshold: float = 0.8
    degradation_levels: Dict[str, Dict[str, int]] = {
        "normal": {"batch_size": 32, "timeout": 30},
        "reduced": {"batch_size": 16, "timeout": 45},
        "minimal": {"batch_size": 8, "timeout": 60},
    }
    min_workers: int = 2
    max_workers: int = 8
    worker_adjustment_interval: int = 60

    class Config:
        env_prefix = "POSE_ESTIMATION_"


settings = Settings()


class MemoryManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.memory_threshold = settings.memory_threshold
        self.gc_threshold = settings.gc_threshold

    async def check_memory(self) -> bool:
        memory_usage = psutil.virtual_memory().percent / 100
        return memory_usage > self.memory_threshold

    async def cleanup(self):
        try:
            # Redis-Cache leeren
            await self.redis_client.flushdb()
            # Temporäre Dateien löschen
            await self.cleanup_temp_files()
            # GC erzwingen
            import gc

            gc.collect()
        except Exception as e:
            logger.error(f"Fehler beim Memory Cleanup: {e}")

    async def cleanup_temp_files(self):
        temp_dir = "/tmp/pose_estimation"
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except Exception as e:
                    logger.error(f"Fehler beim Löschen temporärer Dateien: {e}")

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks()),
        }


class ConcurrencyManager:
    def __init__(self):
        self.base_limit = settings.base_concurrency_limit
        self.max_limit = settings.max_concurrency_limit
        self.min_limit = settings.min_concurrency_limit
        self.current_limit = self.base_limit
        self.semaphore = asyncio.Semaphore(self.current_limit)

    async def adjust_concurrency(self):
        metrics = await self.get_system_metrics()
        cpu_usage = metrics["cpu_usage"]

        if cpu_usage > 80:
            self.current_limit = max(self.min_limit, self.current_limit - 2)
        elif cpu_usage < 50:
            self.current_limit = min(self.max_limit, self.current_limit + 1)

        self.semaphore = asyncio.Semaphore(self.current_limit)

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks()),
        }


class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache_ttl = settings.cache_ttl
        self.max_size = settings.cache_max_size

    async def cache_result(self, key: str, value: Any):
        try:
            await self.redis_client.setex(key, self.cache_ttl, json.dumps(value))
            await self.cleanup_old_entries()
        except Exception as e:
            logger.error(f"Fehler beim Caching: {e}")

    async def get_cache_size(self) -> int:
        try:
            return await self.redis_client.dbsize()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Cache-Größe: {e}")
            return 0

    async def cleanup_old_entries(self):
        try:
            # Lösche alte Einträge basierend auf TTL
            await self.redis_client.execute_command(
                "SCAN", 0, "MATCH", "*", "COUNT", 100
            )
        except Exception as e:
            logger.error(f"Fehler beim Cleanup alter Cache-Einträge: {e}")


class ResourceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.alert_threshold = settings.alert_threshold

    async def monitor_resources(self) -> Dict[str, float]:
        metrics = await self.get_system_metrics()
        self.metrics_history.append(metrics)

        if len(self.metrics_history) > 10:
            self.metrics_history.pop(0)

        if await self.detect_spike():
            await self.trigger_optimization()

        return metrics

    async def detect_spike(self) -> bool:
        if len(self.metrics_history) < 3:
            return False

        recent_metrics = self.metrics_history[-3:]
        cpu_trend = [m["cpu_usage"] for m in recent_metrics]
        memory_trend = [m["memory_usage"] for m in recent_metrics]

        return (
            max(cpu_trend) > self.alert_threshold * 100
            or max(memory_trend) > self.alert_threshold * 100
        )

    async def trigger_optimization(self):
        logger.warning("Resource-Spike erkannt - Optimierung wird ausgelöst")
        # Hier können weitere Optimierungsmaßnahmen implementiert werden

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks()),
        }


class DegradationManager:
    def __init__(self):
        self.degradation_levels = settings.degradation_levels
        self.current_level = "normal"

    async def adjust_service_level(self) -> Dict[str, int]:
        metrics = await self.get_system_metrics()
        memory_usage = metrics["memory_usage"]

        if memory_usage > 90:
            self.current_level = "minimal"
        elif memory_usage > 75:
            self.current_level = "reduced"
        else:
            self.current_level = "normal"

        return self.degradation_levels[self.current_level]

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks()),
        }


class WorkerManager:
    def __init__(self):
        self.min_workers = settings.min_workers
        self.max_workers = settings.max_workers
        self.current_workers = self.min_workers
        self.adjustment_interval = settings.worker_adjustment_interval

    async def adjust_workers(self) -> int:
        metrics = await self.get_system_metrics()
        queue_size = metrics["processing_queue"]

        if queue_size > self.current_workers * 2:
            self.current_workers = min(self.max_workers, self.current_workers + 1)
        elif queue_size < self.current_workers / 2:
            self.current_workers = max(self.min_workers, self.current_workers - 1)

        return self.current_workers

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks()),
        }

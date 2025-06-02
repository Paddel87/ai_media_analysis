import asyncio
import json
import logging
import os
import psutil
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class MemoryManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.memory_threshold = settings.memory_threshold
        self.gc_threshold = settings.gc_threshold

    async def check_memory(self) -> bool:
        metrics = await self.get_system_metrics()
        if metrics["memory_usage"] > self.memory_threshold:
            await self.cleanup()
            return True
        return False

    async def cleanup(self):
        try:
            # Cache leeren
            await self.redis_client.flushdb()
            # Temporäre Dateien löschen
            await self.cleanup_temp_files()
            # GC erzwingen
            import gc
            gc.collect()
        except Exception as e:
            logger.error(f"Fehler beim Memory Cleanup: {e}")

    async def cleanup_temp_files(self):
        temp_dir = settings.temp_dir
        try:
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except Exception as e:
            logger.error(f"Fehler beim Löschen temporärer Dateien: {e}")

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks())
        }

class ConcurrencyManager:
    def __init__(self):
        self.base_limit = settings.base_concurrency_limit
        self.max_limit = settings.max_concurrency_limit
        self.min_limit = settings.min_concurrency_limit
        self.current_limit = self.base_limit
        self.semaphore = asyncio.Semaphore(self.base_limit)

    async def adjust_concurrency(self):
        metrics = await self.get_system_metrics()
        if metrics["cpu_usage"] < 50:
            new_limit = min(self.base_limit * 2, self.max_limit)
        elif metrics["cpu_usage"] > 80:
            new_limit = max(self.base_limit // 2, self.min_limit)
        else:
            new_limit = self.base_limit

        if new_limit != self.current_limit:
            self.current_limit = new_limit
            self.semaphore = asyncio.Semaphore(new_limit)
            logger.info(f"Concurrency-Limit angepasst: {new_limit}")

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks())
        }

class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cache_ttl = settings.cache_ttl
        self.max_cache_size = settings.max_cache_size

    async def cache_result(self, key: str, result: dict):
        try:
            if await self.get_cache_size() > self.max_cache_size:
                await self.cleanup_old_entries()
            await self.redis_client.setex(key, self.cache_ttl, json.dumps(result))
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
            await self.redis_client.execute_command("SCAN", 0, "MATCH", "*", "COUNT", 100)
        except Exception as e:
            logger.error(f"Fehler beim Cleanup alter Cache-Einträge: {e}")

class ResourceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.alert_threshold = settings.alert_threshold

    async def monitor_resources(self) -> Dict[str, Any]:
        metrics = await self.get_system_metrics()
        self.metrics_history.append(metrics)

        if len(self.metrics_history) > 10:
            self.metrics_history.pop(0)

        if self.detect_resource_spike():
            await self.trigger_optimization()

        return metrics

    def detect_resource_spike(self) -> bool:
        if len(self.metrics_history) < 3:
            return False

        recent_metrics = self.metrics_history[-3:]
        cpu_trend = [m["cpu_usage"] for m in recent_metrics]
        memory_trend = [m["memory_usage"] for m in recent_metrics]

        return (max(cpu_trend) > self.alert_threshold * 100 or
                max(memory_trend) > self.alert_threshold * 100)

    async def trigger_optimization(self):
        logger.warning("Resource-Spike erkannt - Optimierung wird ausgelöst")
        # Hier können weitere Optimierungsmaßnahmen implementiert werden

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks())
        }

class DegradationManager:
    def __init__(self):
        self.degradation_levels = settings.degradation_levels
        self.current_level = "normal"

    async def adjust_service_level(self) -> Dict[str, int]:
        metrics = await self.get_system_metrics()
        if metrics["memory_usage"] > settings.memory_threshold:
            self.current_level = "minimal"
        elif metrics["memory_usage"] > settings.gc_threshold:
            self.current_level = "reduced"
        else:
            self.current_level = "normal"

        return self.degradation_levels[self.current_level]

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks())
        }

class WorkerManager:
    def __init__(self):
        self.min_workers = settings.min_workers
        self.max_workers = settings.max_workers
        self.current_workers = self.min_workers

    async def adjust_workers(self) -> int:
        metrics = await self.get_system_metrics()
        queue_size = metrics["processing_queue"]

        if queue_size > 50:
            new_workers = min(self.current_workers + 2, self.max_workers)
        elif queue_size < 10:
            new_workers = max(self.current_workers - 1, self.min_workers)
        else:
            new_workers = self.current_workers

        if new_workers != self.current_workers:
            self.current_workers = new_workers
            logger.info(f"Worker-Anzahl angepasst: {new_workers}")

        return new_workers

    async def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "processing_queue": len(asyncio.all_tasks())
        }

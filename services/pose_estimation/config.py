from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any


class Settings(BaseSettings):
    # Basis-Konfiguration
    model_type: str = "cpu"
    max_workers: int = 4
    memory_limit: int = 1024
    batch_size_limit: int = 100
    processing_timeout: int = 300

    # Redis-Konfiguration
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    redis_db: int = 0

    # Optimierungs-Konfiguration
    memory_threshold: float = 0.8
    gc_threshold: float = 0.9
    alert_threshold: float = 0.85
    cache_ttl: int = 3600
    cache_max_size: int = 1000

    # Concurrency-Konfiguration
    base_concurrency_limit: int = 10
    max_concurrency_limit: int = 50
    min_concurrency_limit: int = 2

    # Worker-Konfiguration
    min_workers: int = 2
    max_workers: int = 8
    worker_adjustment_interval: int = 60

    # Degradation-Levels
    degradation_levels: Dict[str, Dict[str, int]] = {
        "normal": {"batch_size": 50, "concurrency": 10},
        "reduced": {"batch_size": 25, "concurrency": 5},
        "minimal": {"batch_size": 10, "concurrency": 2},
    }

    class Config:
        env_prefix = ""
        case_sensitive = False


def get_settings() -> Settings:
    return Settings()

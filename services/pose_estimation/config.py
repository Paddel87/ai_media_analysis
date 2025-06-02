from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any

class Settings(BaseSettings):
    # Basis-Konfiguration
    model_type: str = "cpu"
    max_workers: int = 4
    memory_limit: int = 1024  # MB
    batch_size_limit: int = 100
    processing_timeout: int = 300  # Sekunden

    # Redis-Konfiguration
    redis_url: str = "redis://localhost:6379"
    batch_expiry: int = 86400  # 24 Stunden
    temp_dir: str = "/tmp/pose_estimation"

    # Optimierungs-Konfiguration
    memory_threshold: int = 1536  # 1.5GB
    gc_threshold: int = 1024  # 1GB
    cache_ttl: int = 3600  # 1 Stunde
    max_cache_size: int = 1000
    alert_threshold: float = 0.8  # 80%

    # Concurrency-Konfiguration
    base_concurrency_limit: int = 10
    max_concurrency_limit: int = 20
    min_concurrency_limit: int = 5

    # Worker-Konfiguration
    min_workers: int = 2
    max_workers: int = 8

    # Degradation-Levels
    degradation_levels: Dict[str, Dict[str, int]] = {
        "normal": {"batch_size": 50, "concurrency": 10},
        "reduced": {"batch_size": 25, "concurrency": 5},
        "minimal": {"batch_size": 10, "concurrency": 2}
    }

    class Config:
        env_prefix = ""
        case_sensitive = False

def get_settings() -> Settings:
    return Settings()

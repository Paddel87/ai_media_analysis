import time
from typing import AsyncGenerator, Dict, Optional
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient


class InMemoryRedis:
    def __init__(self):
        self.store: Dict[str, str] = {}
        self.expiry: Dict[str, float] = {}

    async def get(self, key: str) -> Optional[str]:
        if key in self.store:
            if key in self.expiry and time.time() > self.expiry[key]:
                del self.store[key]
                del self.expiry[key]
                return None
            return self.store[key]
        return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.store[key] = value
        self.expiry[key] = time.time() + ttl

    async def flushdb(self) -> None:
        self.store.clear()
        self.expiry.clear()


@pytest.fixture
def mock_redis() -> InMemoryRedis:
    return InMemoryRedis()


@pytest.fixture
def mock_model() -> AsyncMock:
    model = AsyncMock()
    model.predict.return_value = {
        "keypoints": [[0.5, 0.5, 0.9] for _ in range(17)],
        "scores": [0.9] * 17,
    }
    return model


@pytest.fixture
def test_batch_images() -> list[bytes]:
    return [b"test_image_data" for _ in range(3)]


@pytest.fixture
def mock_redis_error() -> AsyncMock:
    redis_mock = AsyncMock()
    redis_mock.get.side_effect = Exception("Redis connection error")
    return redis_mock


@pytest.fixture
def mock_model_init_error() -> AsyncMock:
    model = AsyncMock()
    model.__init__.side_effect = Exception("Model initialization error")
    return model


@pytest.fixture
def mock_system_metrics() -> Dict[str, float]:
    return {
        "cpu_usage": 50.0,
        "memory_usage": 60.0,
        "processing_queue": 5,
    }


@pytest.fixture
def app() -> FastAPI:
    return FastAPI()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

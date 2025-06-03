"""
Control Service - System Control Interface
Zentrale Steuerung für das AI Media Analysis System
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import redis
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

# FastAPI App
app = FastAPI(
    title="Control Service",
    description="System Control Interface für AI Media Analysis",
    version="1.0.0",
)

# Environment Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 2))
SYSTEM_MODE = os.getenv("SYSTEM_MODE", "production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Global Variables
redis_client = None


class SystemStatus(BaseModel):
    status: str
    mode: str
    timestamp: str
    services: Dict[str, str]
    redis_connected: bool


class ControlCommand(BaseModel):
    command: str
    target: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class ControlResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


async def init_redis():
    """Initialisiert Redis-Verbindung"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        # Test connection
        redis_client.ping()
        logger.info(f"Redis verbunden: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return True
    except Exception as e:
        logger.error(f"Redis Verbindungsfehler: {e}")
        redis_client = None
        return False


@app.on_event("startup")
async def startup_event():
    """Startup Event Handler"""
    logger.info("Control Service startet...")

    # Redis initialisieren
    await init_redis()

    # System-Status in Redis setzen
    if redis_client:
        system_info = {
            "service": "control",
            "status": "running",
            "mode": SYSTEM_MODE,
            "started_at": datetime.now().isoformat(),
        }
        redis_client.hset("system:control", mapping=system_info)

    logger.info("Control Service bereit")


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    redis_status = False
    if redis_client:
        try:
            redis_client.ping()
            redis_status = True
        except:
            redis_status = False

    return {
        "status": "healthy" if redis_status else "degraded",
        "service": "control",
        "redis_connected": redis_status,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/status", response_model=SystemStatus)
async def get_system_status():
    """Systemstatus abrufen"""
    try:
        services = {}
        redis_connected = False

        if redis_client:
            try:
                redis_client.ping()
                redis_connected = True

                # Service-Status aus Redis abrufen
                service_keys = redis_client.keys("system:*")
                for key in service_keys:
                    service_name = key.split(":")[1]
                    service_data = redis_client.hgetall(key)
                    services[service_name] = service_data.get("status", "unknown")

            except Exception as e:
                logger.error(f"Redis Status-Fehler: {e}")

        return SystemStatus(
            status="online",
            mode=SYSTEM_MODE,
            timestamp=datetime.now().isoformat(),
            services=services,
            redis_connected=redis_connected,
        )

    except Exception as e:
        logger.error(f"Status-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/command", response_model=ControlResponse)
async def execute_command(command: ControlCommand, background_tasks: BackgroundTasks):
    """System-Befehl ausführen"""
    try:
        logger.info(f"Befehl empfangen: {command.command}")

        if not redis_client:
            return ControlResponse(success=False, message="Redis nicht verfügbar")

        # Befehl verarbeiten
        if command.command == "ping":
            return ControlResponse(
                success=True,
                message="pong",
                data={"timestamp": datetime.now().isoformat()},
            )

        elif command.command == "system_info":
            system_data = redis_client.hgetall("system:control")
            return ControlResponse(
                success=True, message="System-Info abgerufen", data=system_data
            )

        elif command.command == "restart_service" and command.target:
            # Service-Restart-Befehl in Redis Queue
            restart_data = {
                "target": command.target,
                "timestamp": datetime.now().isoformat(),
                "parameters": command.parameters or {},
            }
            redis_client.lpush("control:restart_queue", str(restart_data))

            return ControlResponse(
                success=True, message=f"Restart-Befehl für {command.target} eingereicht"
            )

        else:
            return ControlResponse(
                success=False, message=f"Unbekannter Befehl: {command.command}"
            )

    except Exception as e:
        logger.error(f"Befehl-Fehler: {e}")
        return ControlResponse(
            success=False, message=f"Fehler bei Befehlsausführung: {str(e)}"
        )


@app.get("/services")
async def list_services():
    """Verfügbare Services auflisten"""
    try:
        if not redis_client:
            return {"services": [], "redis_connected": False}

        service_keys = redis_client.keys("system:*")
        services = []

        for key in service_keys:
            service_name = key.split(":")[1]
            service_data = redis_client.hgetall(key)
            services.append(
                {
                    "name": service_name,
                    "status": service_data.get("status", "unknown"),
                    "mode": service_data.get("mode", "unknown"),
                    "started_at": service_data.get("started_at", "unknown"),
                }
            )

        return {"services": services, "count": len(services), "redis_connected": True}

    except Exception as e:
        logger.error(f"Service-Listen-Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=LOG_LEVEL.lower())

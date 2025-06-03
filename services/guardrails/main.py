import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("guardrails")

app = FastAPI(
    title="Guardrails Service",
    description="Service für Sicherheitskontrollen und Validierungen",
)


class GuardrailService:
    def __init__(self):
        self.config = self.load_config()
        self.blocked_patterns = self.load_blocked_patterns()
        self.rate_limits = {}

    def load_config(self) -> Dict:
        """Lädt die Guardrail-Konfiguration"""
        try:
            config_path = os.getenv("GUARDRAIL_CONFIG", "./config/guardrails.json")
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return {
                "max_file_size_mb": 100,
                "allowed_mime_types": ["image/jpeg", "image/png", "video/mp4"],
                "max_batch_size": 10,
                "rate_limit_per_minute": 60,
            }

    def load_blocked_patterns(self) -> List[str]:
        """Lädt blockierte Muster"""
        try:
            patterns_path = os.getenv(
                "BLOCKED_PATTERNS", "./config/blocked_patterns.json"
            )
            with open(patterns_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der blockierten Muster: {str(e)}")
            return []

    def validate_request(self, request: Request) -> Dict:
        """
        Validiert eine Anfrage
        """
        try:
            # Rate Limiting
            client_ip = request.client.host
            current_time = datetime.utcnow()

            if client_ip in self.rate_limits:
                last_request, count = self.rate_limits[client_ip]
                if (current_time - last_request).total_seconds() < 60:
                    if count >= self.config["rate_limit_per_minute"]:
                        raise HTTPException(
                            status_code=429, detail="Rate limit überschritten"
                        )
                    self.rate_limits[client_ip] = (last_request, count + 1)
                else:
                    self.rate_limits[client_ip] = (current_time, 1)
            else:
                self.rate_limits[client_ip] = (current_time, 1)

            # Content-Type Validierung
            content_type = request.headers.get("content-type", "")
            if content_type not in self.config["allowed_mime_types"]:
                raise HTTPException(
                    status_code=415,
                    detail=f"Nicht unterstützter Content-Type: {content_type}",
                )

            # Content-Length Validierung
            content_length = int(request.headers.get("content-length", 0))
            max_size = self.config["max_file_size_mb"] * 1024 * 1024
            if content_length > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"Datei zu groß. Maximum: {self.config['max_file_size_mb']}MB",
                )

            return {"status": "valid"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Fehler bei der Anfragevalidierung: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def validate_content(self, content: bytes) -> Dict:
        """
        Validiert den Inhalt
        """
        try:
            # Hash-Berechnung für Duplikaterkennung
            content_hash = hashlib.sha256(content).hexdigest()

            # MIME-Type Validierung
            mime_type = self.detect_mime_type(content)
            if mime_type not in self.config["allowed_mime_types"]:
                raise HTTPException(
                    status_code=415,
                    detail=f"Nicht unterstützter MIME-Type: {mime_type}",
                )

            # Größenvalidierung
            if len(content) > self.config["max_file_size_mb"] * 1024 * 1024:
                raise HTTPException(
                    status_code=413,
                    detail=f"Datei zu groß. Maximum: {self.config['max_file_size_mb']}MB",
                )

            return {
                "status": "valid",
                "mime_type": mime_type,
                "size_bytes": len(content),
                "content_hash": content_hash,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Fehler bei der Inhaltsvalidierung: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def validate_batch(self, items: List[bytes]) -> Dict:
        """
        Validiert einen Batch von Items
        """
        try:
            if len(items) > self.config["max_batch_size"]:
                raise HTTPException(
                    status_code=413,
                    detail=f"Batch zu groß. Maximum: {self.config['max_batch_size']} Items",
                )

            results = []
            for item in items:
                result = self.validate_content(item)
                results.append(result)

            return {"status": "valid", "items": results}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Fehler bei der Batch-Validierung: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def detect_mime_type(self, content: bytes) -> str:
        """
        Erkennt den MIME-Type des Inhalts
        """
        # Einfache MIME-Type-Erkennung
        if content.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        elif content.startswith(b"\x89PNG"):
            return "image/png"
        elif content.startswith(b"\x00\x00\x00\x18ftypmp42"):
            return "video/mp4"
        return "application/octet-stream"


# Service-Instanz erstellen
guardrail_service = GuardrailService()


class ContentValidationRequest(BaseModel):
    content: bytes


class BatchValidationRequest(BaseModel):
    items: List[bytes]


@app.post("/validate/request")
async def validate_request(request: Request):
    """
    Validiert eine Anfrage
    """
    try:
        return guardrail_service.validate_request(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate/content")
async def validate_content(request: ContentValidationRequest):
    """
    Validiert den Inhalt
    """
    try:
        return guardrail_service.validate_content(request.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate/batch")
async def validate_batch(request: BatchValidationRequest):
    """
    Validiert einen Batch
    """
    try:
        return guardrail_service.validate_batch(request.items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

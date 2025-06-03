import base64
import logging
import uuid
from datetime import datetime
from typing import Dict, List

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsfw_detection")

app = FastAPI(
    title="NSFW Detection Service", description="Service für NSFW-Erkennung mit CLIP"
)


class NSFWService:
    def __init__(self):
        self.clip_service_url = "http://clip-service:8000"
        self.nsfw_categories = [
            "nude",
            "explicit",
            "sexual",
            "violence",
            "gore",
            "disturbing",
            "inappropriate",
            "adult content",
        ]

    async def analyze_image(self, image_data: bytes) -> Dict:
        """
        Analysiert ein Bild auf NSFW-Inhalte
        """
        try:
            # CLIP-Analyse durchführen
            response = requests.post(
                f"{self.clip_service_url}/analyze",
                json={
                    "image_data": base64.b64encode(image_data).decode(),
                    "text_queries": self.nsfw_categories,
                },
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500, detail="CLIP-Service nicht erreichbar"
                )

            results = response.json()

            # Ergebnisse formatieren
            nsfw_score = max(results.values())
            detected_categories = {
                category: score
                for category, score in results.items()
                if score > 0.5  # Schwellenwert für Kategorien
            }

            return {
                "nsfw_score": nsfw_score,
                "detected_categories": detected_categories,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis_id": str(uuid.uuid4()),
            }

        except Exception as e:
            logger.error(f"Fehler bei der NSFW-Analyse: {str(e)}")
            raise

    async def analyze_batch(self, images: List[bytes]) -> List[Dict]:
        """
        Analysiert mehrere Bilder auf NSFW-Inhalte
        """
        results = []
        for image_data in images:
            try:
                result = await self.analyze_image(image_data)
                results.append(result)
            except Exception as e:
                logger.error(f"Fehler bei der Batch-Analyse: {str(e)}")
                results.append(
                    {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
                )
        return results


# Service-Instanz erstellen
nsfw_service = NSFWService()


class ImageAnalysisRequest(BaseModel):
    image_data: bytes


class BatchAnalysisRequest(BaseModel):
    images: List[bytes]


@app.post("/analyze")
async def analyze_image(request: ImageAnalysisRequest):
    """
    Analysiert ein einzelnes Bild
    """
    try:
        return await nsfw_service.analyze_image(request.image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analysiert mehrere Bilder
    """
    try:
        return await nsfw_service.analyze_batch(request.images)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # CLIP-Service Health Check
        response = requests.get(f"{nsfw_service.clip_service_url}/health")
        if response.status_code != 200:
            return {"status": "unhealthy", "clip_service": "unavailable"}
        return {"status": "healthy", "clip_service": "available"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

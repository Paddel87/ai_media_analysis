"""
NSFW Detection Service - Einfaches Beispiel mit Insights-Integration
Zeigt perfekte Integration der Erkenntnisse-Datenbank
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import der Insights-Services
sys.path.append("../")
from common.insights_service import insights_service

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsfw_service")

app = FastAPI(
    title="NSFW Detection Service",
    description="Service für NSFW-Erkennung mit Insights-Integration",
)


class NSFWAnalysisRequest(BaseModel):
    """Request für NSFW-Analyse."""
    image_data: bytes
    job_id: str
    media_id: str
    media_filename: str
    media_type: str = "image"


class NSFWAnalysisResult(BaseModel):
    """Ergebnis der NSFW-Analyse."""
    is_nsfw: bool
    nsfw_score: float
    categories: List[str]
    confidence: float
    analysis_time: float


class NSFWService:
    """Einfacher NSFW-Detection Service mit Insights-Integration."""

    def __init__(self):
        self.confidence_threshold = 0.7

    async def analyze_image(self, request: NSFWAnalysisRequest) -> NSFWAnalysisResult:
        """
        Analysiert ein Bild auf NSFW-Inhalte.
        """
        start_time = datetime.now()

        try:
            # Simulierte NSFW-Analyse (in Realität: ML-Model)
            nsfw_score = await self._detect_nsfw_content(request.image_data)
            is_nsfw = nsfw_score > self.confidence_threshold
            categories = self._classify_content_categories(nsfw_score)

            # Ergebnis erstellen
            result = NSFWAnalysisResult(
                is_nsfw=is_nsfw,
                nsfw_score=nsfw_score,
                categories=categories,
                confidence=nsfw_score,
                analysis_time=(datetime.now() - start_time).total_seconds()
            )

            # ✅ INSIGHTS-INTEGRATION: Erkenntnis speichern
            await self._save_nsfw_insight(request, result)

            logger.info(f"✅ NSFW analysis completed: {request.media_id} - NSFW: {is_nsfw}")
            return result

        except Exception as e:
            logger.error(f"❌ NSFW analysis failed: {str(e)}")
            raise

    async def _detect_nsfw_content(self, image_data: bytes) -> float:
        """Simulierte NSFW-Erkennung."""
        # In Realität: ML-Model für NSFW-Detection
        # Hier: Einfache Simulation basierend auf Datengröße
        score = min(len(image_data) / 1000000, 1.0)  # Größere Bilder = höhere NSFW-Chance (Demo)
        return score

    def _classify_content_categories(self, nsfw_score: float) -> List[str]:
        """Klassifiziert NSFW-Kategorien."""
        categories: List[str] = []

        if nsfw_score > 0.9:
            categories.extend(["explicit", "adult"])
        elif nsfw_score > 0.7:
            categories.extend(["suggestive", "mature"])
        elif nsfw_score > 0.5:
            categories.append("questionable")
        else:
            categories.append("safe")

        return categories

    async def _save_nsfw_insight(self, request: NSFWAnalysisRequest, result: NSFWAnalysisResult):
        """
        ✅ KERNELEMENT: Speichert NSFW-Erkenntnis in Insights-Datenbank.

        Dies ist das perfekte Beispiel, wie JEDER Service seine Erkenntnisse
        in die durchsuchbare Datenbank einträgt.
        """
        try:
            # NSFW-Daten für Insights formatieren
            nsfw_data = {
                "nsfw_score": result.nsfw_score,
                "is_nsfw": result.is_nsfw,
                "categories": result.categories,
                "analysis_time": result.analysis_time,
                "threshold_used": self.confidence_threshold
            }

            # ⭐ INSIGHTS-SERVICE AUFRUFEN
            insight_id = insights_service.add_nsfw_detection(
                job_id=request.job_id,
                media_id=request.media_id,
                media_filename=request.media_filename,
                media_type=request.media_type,
                nsfw_data=nsfw_data,
                confidence=result.confidence,
                media_timestamp=None  # Bei Bildern nicht relevant
            )

            logger.info(f"✅ NSFW insight saved to database: {insight_id}")

        except Exception as e:
            logger.error(f"❌ Failed to save NSFW insight: {str(e)}")
            # WICHTIG: Nicht kritisch - Hauptfunktion läuft weiter


# Service-Instanz
nsfw_service = NSFWService()


@app.post("/analyze", response_model=NSFWAnalysisResult)
async def analyze_nsfw(request: NSFWAnalysisRequest):
    """
    Analysiert ein Bild auf NSFW-Inhalte.

    Die Erkenntnis wird automatisch in der Insights-Datenbank gespeichert!
    """
    return await nsfw_service.analyze_image(request)


@app.get("/health")
async def health_check():
    """Health Check."""
    return {"status": "healthy", "service": "nsfw_detection"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)

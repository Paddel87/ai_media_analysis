"""
🔗 SERVICE INTEGRATION GUIDE
Vollständige Anleitung: Wie gelangen Erkenntnisse aus Services in die Datenbank?

Dieses Dokument zeigt die exakte Integration für alle AI-Services.
"""

import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# SCHRITT 1: Import der Insights-Services
sys.path.append("../")
from insights_service import insights_service


# =====================================================================
# INTEGRATION PATTERN: 3 SCHRITTE FÜR JEDEN SERVICE
# =====================================================================

class ServiceIntegrationExample:
    """
    Zeigt die Standard-Integration für beliebige AI-Services.
    """

    async def analyze_media_with_insights(
        self,
        media_data: bytes,
        job_id: str,
        media_id: str,
        media_filename: str,
        service_type: str
    ):
        """
        UNIVERSAL PATTERN für Service-Integration.
        """

        # 🔍 SCHRITT 1: Normale AI-Analyse durchführen
        analysis_result = await self._perform_ai_analysis(media_data)

        # 📊 SCHRITT 2: Service-spezifische Verarbeitung
        processed_result = self._process_analysis_result(analysis_result)

        # ✅ SCHRITT 3: Erkenntnis in Insights-DB speichern
        await self._save_insight_to_database(
            processed_result, job_id, media_id, media_filename, service_type
        )

        return processed_result

    async def _perform_ai_analysis(self, media_data: bytes) -> Dict[str, Any]:
        """Führt die eigentliche AI-Analyse durch."""
        # Hier passiert die normale Service-Logik
        # - ML-Model aufrufen
        # - API-Calls an externe Services
        # - Datenverarbeitung
        return {"result": "analysis_data"}

    def _process_analysis_result(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet das Analyseergebnis für den Service."""
        # Service-spezifische Nachverarbeitung
        return analysis_result

    async def _save_insight_to_database(
        self,
        result: Dict[str, Any],
        job_id: str,
        media_id: str,
        media_filename: str,
        service_type: str
    ):
        """
        ⭐ KERNELEMENT: Speichert Erkenntnis in Insights-Datenbank.

        DIES IST DER EINZIGE CODE, DEN JEDER SERVICE HINZUFÜGEN MUSS!
        """
        try:
            if service_type == "person_detection":
                await self._save_person_insight(result, job_id, media_id, media_filename)
            elif service_type == "nsfw_detection":
                await self._save_nsfw_insight(result, job_id, media_id, media_filename)
            elif service_type == "audio_transcription":
                await self._save_audio_insight(result, job_id, media_id, media_filename)
            elif service_type == "clothing_analysis":
                await self._save_clothing_insight(result, job_id, media_id, media_filename)
            # ... weitere Service-Typen

        except Exception as e:
            # WICHTIG: Insights-Fehler dürfen Service nicht zum Absturz bringen
            print(f"❌ Insight save failed: {e}")

    # =====================================================================
    # SERVICE-SPEZIFISCHE INSIGHTS-INTEGRATION
    # =====================================================================

    async def _save_person_insight(self, result: Dict[str, Any], job_id: str, media_id: str, media_filename: str):
        """Integration für Person Detection Services."""

        person_data = {
            "display_name": result.get("person_name", "Unknown Person"),
            "emotions": result.get("emotions", []),
            "confidence": result.get("confidence", 0.0),
            "face_id": result.get("face_id"),
            "age_estimate": result.get("age", 0)
        }

        insight_id = insights_service.add_person_detection(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type="video",  # oder "image"
            person_data=person_data,
            confidence=result.get("confidence", 0.0),
            media_timestamp=result.get("timestamp")
        )

        print(f"✅ Person insight saved: {insight_id}")

    async def _save_nsfw_insight(self, result: Dict[str, Any], job_id: str, media_id: str, media_filename: str):
        """Integration für NSFW Detection Services."""

        nsfw_data = {
            "nsfw_score": result.get("nsfw_score", 0.0),
            "is_nsfw": result.get("is_nsfw", False),
            "categories": result.get("categories", []),
            "detected_objects": result.get("objects", [])
        }

        insight_id = insights_service.add_nsfw_detection(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type="image",
            nsfw_data=nsfw_data,
            confidence=result.get("confidence", 0.0)
        )

        print(f"✅ NSFW insight saved: {insight_id}")

    async def _save_audio_insight(self, result: Dict[str, Any], job_id: str, media_id: str, media_filename: str):
        """Integration für Audio Transcription Services."""

        transcription_data = {
            "text": result.get("transcript", ""),
            "language": result.get("language", "unknown"),
            "word_count": len(result.get("transcript", "").split()),
            "confidence": result.get("confidence", 0.0),
            "speaker_count": result.get("speakers", 1)
        }

        insight_id = insights_service.add_audio_transcription(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            transcription_data=transcription_data,
            confidence=result.get("confidence", 0.0),
            media_timestamp=result.get("timestamp")
        )

        print(f"✅ Audio insight saved: {insight_id}")

    async def _save_clothing_insight(self, result: Dict[str, Any], job_id: str, media_id: str, media_filename: str):
        """Integration für Clothing Analysis Services."""

        clothing_data = {
            "detected_clothing": result.get("clothing_items", []),
            "overall_style": result.get("style", "casual"),
            "materials": result.get("materials", []),
            "colors": result.get("colors", []),
            "total_items": len(result.get("clothing_items", []))
        }

        insight_id = insights_service.add_clothing_analysis(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type="image",
            clothing_data=clothing_data,
            confidence=result.get("confidence", 0.0)
        )

        print(f"✅ Clothing insight saved: {insight_id}")


# =====================================================================
# RETROFIT-INTEGRATION: Bestehende Services nachrüsten
# =====================================================================

class ExistingServiceRetrofit:
    """
    Zeigt, wie bestehende Services mit minimalen Änderungen
    die Insights-Integration bekommen.
    """

    async def existing_analyze_function(self, media_data: bytes, job_id: str, media_id: str):
        """
        VORHER: Bestehende Analyze-Funktion ohne Insights.
        """
        # Normale Service-Logik (bleibt unverändert)
        analysis_result = await self._do_complex_ai_analysis(media_data)

        # Service-interne Speicherung (bleibt unverändert)
        await self._save_to_redis(analysis_result)
        await self._update_dossier(analysis_result)

        return analysis_result

    async def retrofitted_analyze_function(self, media_data: bytes, job_id: str, media_id: str, media_filename: str):
        """
        NACHHER: Gleiche Funktion + 3 Zeilen für Insights.
        """
        # Normale Service-Logik (unverändert)
        analysis_result = await self._do_complex_ai_analysis(media_data)

        # Service-interne Speicherung (unverändert)
        await self._save_to_redis(analysis_result)
        await self._update_dossier(analysis_result)

        # ✅ NEU: Nur diese 3 Zeilen hinzufügen
        try:
            await self._save_to_insights_db(analysis_result, job_id, media_id, media_filename)
        except Exception as e:
            print(f"Insights save failed: {e}")  # Service läuft weiter

        return analysis_result

    async def _do_complex_ai_analysis(self, media_data: bytes) -> Dict[str, Any]:
        """Simuliert komplexe bestehende AI-Analyse."""
        return {"complex": "analysis_result"}

    async def _save_to_redis(self, result: Dict[str, Any]):
        """Simuliert bestehende Redis-Speicherung."""
        pass

    async def _update_dossier(self, result: Dict[str, Any]):
        """Simuliert bestehende Dossier-Updates."""
        pass

    async def _save_to_insights_db(self, result: Dict[str, Any], job_id: str, media_id: str, media_filename: str):
        """Die EINE neue Funktion für Insights-Integration."""

        # Je nach Service-Typ den passenden add_xxx() aufrufen
        if "person" in str(result):
            insights_service.add_person_detection(
                job_id=job_id,
                media_id=media_id,
                media_filename=media_filename,
                media_type="video",
                person_data=result,
                confidence=result.get("confidence", 0.0)
            )


# =====================================================================
# ORCHESTRIERUNG: Job Manager Integration
# =====================================================================

class JobManagerIntegration:
    """
    Zeigt, wie der Job Manager automatisch alle Service-Erkenntnisse sammelt.
    """

    async def process_uc001_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        UC-001 Job Processing mit automatischer Insights-Sammlung.
        """
        job_id = job_data["job_id"]
        media_path = job_data["media_path"]
        media_filename = job_data.get("media_filename", "unknown.mp4")

        results = {}

        # 🎯 Verschiedene Services aufrufen
        if job_data.get("enable_person_detection"):
            person_result = await self._call_person_service(media_path, job_id, media_filename)
            results["person_detection"] = person_result

        if job_data.get("enable_nsfw_detection"):
            nsfw_result = await self._call_nsfw_service(media_path, job_id, media_filename)
            results["nsfw_detection"] = nsfw_result

        if job_data.get("enable_audio_transcription"):
            audio_result = await self._call_audio_service(media_path, job_id, media_filename)
            results["audio_transcription"] = audio_result

        # ✅ Alle Services speichern automatisch in Insights-DB
        # Keine zusätzliche Orchestrierung nötig!

        return results

    async def _call_person_service(self, media_path: str, job_id: str, media_filename: str) -> Dict[str, Any]:
        """Ruft Person Detection Service auf (der speichert automatisch Insights)."""
        # HTTP-Call an Person Service
        # Service speichert automatisch via insights_service.add_person_detection()
        return {"status": "completed", "persons_found": 3}

    async def _call_nsfw_service(self, media_path: str, job_id: str, media_filename: str) -> Dict[str, Any]:
        """Ruft NSFW Service auf (der speichert automatisch Insights)."""
        # HTTP-Call an NSFW Service
        # Service speichert automatisch via insights_service.add_nsfw_detection()
        return {"status": "completed", "is_nsfw": False}

    async def _call_audio_service(self, media_path: str, job_id: str, media_filename: str) -> Dict[str, Any]:
        """Ruft Audio Service auf (der speichert automatisch Insights)."""
        # HTTP-Call an Audio Service
        # Service speichert automatisch via insights_service.add_audio_transcription()
        return {"status": "completed", "transcript": "Hello world"}


# =====================================================================
# ZUSAMMENFASSUNG: SO EINFACH IST DIE INTEGRATION
# =====================================================================

"""
🎯 ANTWORT AUF IHRE FRAGE: "Wie gelangen Erkenntnisse in die Datenbank?"

1️⃣ IMPORT HINZUFÜGEN (1 Zeile):
   from common.insights_service import insights_service

2️⃣ NACH JEDER ANALYSE AUFRUFEN (3 Zeilen):
   try:
       insights_service.add_person_detection(job_id, media_id, filename, data, confidence)
   except Exception as e:
       logger.error(f"Insights save failed: {e}")

3️⃣ FERTIG!
   - Erkenntnis ist sofort in SQLite gespeichert
   - FTS5-Index macht sie durchsuchbar
   - Web-Interface zeigt sie an
   - Benutzer können suchen und exportieren

📊 KEINE ORCHESTRIERUNG NÖTIG:
   - Jeder Service speichert eigenständig
   - Job Manager muss nichts zusätzlich tun
   - Insights sammeln sich automatisch
   - Web-Interface zeigt alle gesammelten Erkenntnisse

🔧 RETROFIT BESTEHENDE SERVICES:
   - Nur 4 Zeilen Code pro Service hinzufügen
   - Bestehende Logik bleibt unverändert
   - Fehler-sicher: Insights-Fehler crashen Service nicht
   - Funktioniert parallel zu bestehenden Speichermechanismen
"""

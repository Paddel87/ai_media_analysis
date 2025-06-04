"""
Insights Service - Integration der durchsuchbaren Erkenntnisse-Datenbank.
Sammelt und speichert alle Analyseergebnisse aus verschiedenen AI-Services.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

# Docker-kompatible Imports
try:
    from data_schema.insights_database import (
        InsightEntry,
        InsightQuery,
        InsightsDatabase,
        InsightType,
    )
except ImportError:
    try:
        from data_schema_root.insights_database import (
            InsightEntry,
            InsightQuery,
            InsightsDatabase,
            InsightType,
        )
    except ImportError:
        # Fallback für lokale Entwicklung
        import sys
        sys.path.append("../../")
        from data_schema.insights_database import (
            InsightEntry,
            InsightQuery,
            InsightsDatabase,
            InsightType,
        )


class InsightsService:
    """
    Service zur Verwaltung der Erkenntnisse-Datenbank.
    Sammelt Ergebnisse aus allen AI-Services und macht sie durchsuchbar.
    """

    def __init__(self, db_path: str = "data/insights.db"):
        self.db = InsightsDatabase(db_path)

    def add_person_detection(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        person_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Personenerkennung zur Datenbank hinzu."""

        person_name = person_data.get("display_name", "Unbekannte Person")
        emotion_summary = ", ".join(person_data.get("emotions", []))

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.PERSON_DETECTION,
            category="face_recognition",
            tags=["person", "face", "detection"],
            media_timestamp=media_timestamp,
            title=f"Person erkannt: {person_name}",
            description=f"Person '{person_name}' mit Emotionen: {emotion_summary}",
            confidence=confidence,
            raw_data=person_data,
        )

        return self.db.add_insight(insight)

    def add_emotion_analysis(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        emotion_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Emotionsanalyse zur Datenbank hinzu."""

        dominant_emotion = max(emotion_data.get("emotions", {}), key=emotion_data.get("emotions", {}).get, default="neutral")
        emotion_score = emotion_data.get("emotions", {}).get(dominant_emotion, 0.0)

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.EMOTION_ANALYSIS,
            category="emotion_detection",
            tags=["emotion", dominant_emotion, "facial_analysis"],
            media_timestamp=media_timestamp,
            title=f"Emotion erkannt: {dominant_emotion.title()}",
            description=f"Dominante Emotion: {dominant_emotion} (Konfidenz: {emotion_score:.2f})",
            confidence=confidence,
            raw_data=emotion_data,
        )

        return self.db.add_insight(insight)

    def add_restraint_detection(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        restraint_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Restraint-Erkennung zur Datenbank hinzu."""

        restraint_types = restraint_data.get("detected_restraints", [])
        restraint_summary = ", ".join(restraint_types) if restraint_types else "Allgemeine Erkennung"

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.RESTRAINT_DETECTION,
            category="content_moderation",
            tags=["restraint", "bdsm", "content_warning"] + restraint_types,
            media_timestamp=media_timestamp,
            title=f"Restraints erkannt: {restraint_summary}",
            description=f"Erkannte Fesselungen/Restraints: {restraint_summary}",
            confidence=confidence,
            raw_data=restraint_data,
        )

        return self.db.add_insight(insight)

    def add_clothing_analysis(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        clothing_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Kleidungsanalyse zur Datenbank hinzu."""

        clothing_items = clothing_data.get("detected_clothing", [])
        clothing_summary = ", ".join(clothing_items[:3])  # Nur die ersten 3 für Übersicht

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.CLOTHING_ANALYSIS,
            category="clothing_classification",
            tags=["clothing", "fashion"] + clothing_items[:5],  # Top 5 als Tags
            media_timestamp=media_timestamp,
            title=f"Kleidung erkannt: {clothing_summary}",
            description=f"Erkannte Kleidungsstücke: {clothing_summary}{'...' if len(clothing_items) > 3 else ''}",
            confidence=confidence,
            raw_data=clothing_data,
        )

        return self.db.add_insight(insight)

    def add_audio_transcription(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        transcription_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Audio-Transkription zur Datenbank hinzu."""

        transcript_text = transcription_data.get("text", "")
        language = transcription_data.get("language", "unknown")
        word_count = len(transcript_text.split()) if transcript_text else 0

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type="audio",
            insight_type=InsightType.AUDIO_TRANSCRIPTION,
            category="speech_to_text",
            tags=["audio", "transcript", "speech", language],
            media_timestamp=media_timestamp,
            title=f"Audio transkribiert ({language}): {word_count} Wörter",
            description=transcript_text[:200] + ("..." if len(transcript_text) > 200 else ""),
            confidence=confidence,
            raw_data=transcription_data,
        )

        return self.db.add_insight(insight)

    def add_video_context(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        context_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt Video-Kontext-Analyse zur Datenbank hinzu."""

        scene_description = context_data.get("scene_description", "")
        context_summary = context_data.get("context_summary", "")

        # Verwende context_summary für eine vollständigere Beschreibung
        full_description = f"{scene_description} {context_summary}".strip()

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type="video",
            insight_type=InsightType.VIDEO_CONTEXT,
            category="scene_understanding",
            tags=["video", "context", "scene", "llm_analysis"],
            media_timestamp=media_timestamp,
            title="Video-Kontext analysiert",
            description=full_description[:200] + ("..." if len(full_description) > 200 else ""),
            confidence=confidence,
            raw_data=context_data,
        )

        return self.db.add_insight(insight)

    def add_nsfw_detection(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        nsfw_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt NSFW-Erkennung zur Datenbank hinzu."""

        nsfw_score = nsfw_data.get("nsfw_score", 0.0)
        is_nsfw = nsfw_data.get("is_nsfw", False)
        categories = nsfw_data.get("categories", [])

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.NSFW_DETECTION,
            category="content_moderation",
            tags=["nsfw", "content_warning"] + (categories if is_nsfw else ["safe"]),
            media_timestamp=media_timestamp,
            title=f"NSFW-Check: {'⚠️ NSFW' if is_nsfw else '✅ Sicher'}",
            description=f"NSFW Score: {nsfw_score:.2f}, Kategorien: {', '.join(categories) if categories else 'Keine'}",
            confidence=confidence,
            raw_data=nsfw_data,
        )

        return self.db.add_insight(insight)

    def add_ocr_text(
        self,
        job_id: str,
        media_id: str,
        media_filename: str,
        media_type: str,
        ocr_data: Dict[str, Any],
        confidence: float,
        media_timestamp: Optional[float] = None,
    ) -> str:
        """Fügt OCR-Texterkennung zur Datenbank hinzu."""

        extracted_text = ocr_data.get("text", "")
        language = ocr_data.get("language", "unknown")
        text_length = len(extracted_text)

        insight = InsightEntry(
            job_id=job_id,
            media_id=media_id,
            media_filename=media_filename,
            media_type=media_type,
            insight_type=InsightType.OCR_TEXT,
            category="text_extraction",
            tags=["ocr", "text", "recognition", language],
            media_timestamp=media_timestamp,
            title=f"Text erkannt ({language}): {text_length} Zeichen",
            description=extracted_text[:200] + ("..." if len(extracted_text) > 200 else ""),
            confidence=confidence,
            raw_data=ocr_data,
        )

        return self.db.add_insight(insight)

    def search_insights(
        self,
        search_text: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        job_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Durchsucht die Erkenntnisse-Datenbank."""

        # InsightType-Enum konvertieren
        enum_types: Optional[List[InsightType]] = None
        if insight_types:
            enum_types = []
            for insight_type in insight_types:
                try:
                    enum_types.append(InsightType(insight_type))
                except ValueError:
                    pass  # Ungültige Typen ignorieren

        query = InsightQuery(
            search_text=search_text,
            insight_types=enum_types,
            tags=tags,
            start_date=start_date,
            end_date=end_date,
            job_ids=[job_id] if job_id else None,
            limit=limit,
        )

        return self.db.search(query)

    def get_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung aller gespeicherten Erkenntnisse zurück."""
        return self.db.get_insights_summary()

    def get_job_insights(self, job_id: str) -> List[Dict[str, Any]]:
        """Gibt alle Erkenntnisse für einen bestimmten Job zurück."""
        query = InsightQuery(job_ids=[job_id], limit=1000)  # Alle für den Job
        return self.db.search(query)

    def get_media_insights(self, media_id: str) -> List[Dict[str, Any]]:
        """Gibt alle Erkenntnisse für ein bestimmtes Medium zurück."""
        query = InsightQuery(limit=1000)  # Alle suchen
        all_results = self.db.search(query)

        # Nach media_id filtern
        return [result for result in all_results if result.get("media_id") == media_id]

    def delete_job_insights(self, job_id: str) -> int:
        """Löscht alle Erkenntnisse für einen Job (für Cleanup)."""
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute("DELETE FROM insights WHERE job_id = ?", (job_id,))
            deleted_count = cursor.rowcount
            conn.commit()
            return deleted_count


# Globale Instanz für einfache Nutzung
insights_service = InsightsService()

"""
🔍 Insights-basierter Personen-Dossier Service
Erweiterte Personen-Analyse mit komplexen Suchabfragen

Beispiel: "Blondine + Shibari" zeigt alle blonden Frauen in Shibari-Fesselungen
"""

import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# Vereinfachte Insights-Integration ohne externe Dependencies
class MockInsightsService:
    """Mock Service für Demonstration ohne DB-Dependencies."""

    def search_insights(self, search_text=None, limit=50, **kwargs):
        """Mock-Implementierung für Demo-Zwecke."""
        # Generiere Mock-Daten für Demonstration
        mock_insights = [
            {
                "insight_id": "1",
                "job_id": "job_001",
                "media_filename": "video_001.mp4",
                "insight_type": "person_detection",
                "raw_data": {
                    "person_id": "person_001",
                    "display_name": "Blonde Person",
                    "hair_color": "blonde",
                    "age_estimate": 25,
                    "emotions": ["happy", "surprised"],
                    "embedding": [0.1] * 512
                },
                "confidence": 0.85,
                "created_at": "2024-01-01T10:00:00"
            },
            {
                "insight_id": "2",
                "job_id": "job_001",
                "media_filename": "video_001.mp4",
                "insight_type": "restraint_detection",
                "raw_data": {
                    "person_id": "person_001",
                    "detected_restraints": ["shibari", "rope_bondage"],
                    "bondage_styles": ["japanese_bondage", "artistic_bondage"]
                },
                "confidence": 0.92,
                "created_at": "2024-01-01T10:00:00"
            },
            {
                "insight_id": "3",
                "job_id": "job_002",
                "media_filename": "video_002.mp4",
                "insight_type": "person_detection",
                "raw_data": {
                    "person_id": "person_002",
                    "display_name": "Brunette Person",
                    "hair_color": "brunette",
                    "age_estimate": 28,
                    "emotions": ["neutral", "pleasure"],
                    "embedding": [0.2] * 512
                },
                "confidence": 0.88,
                "created_at": "2024-01-01T11:00:00"
            }
        ]

        # Einfache Filterung basierend auf search_text
        if search_text:
            filtered = []
            for insight in mock_insights:
                insight_str = str(insight).lower()
                if search_text.lower() in insight_str:
                    filtered.append(insight)
            return filtered[:limit]

        return mock_insights[:limit]

# Mock Service verwenden
insights_service = MockInsightsService()

class PersonProfile(BaseModel):
    """Vollständiges Personen-Profil basierend auf allen Insights."""
    person_id: str
    display_name: str
    confidence_score: float

    # Erscheinungsmerkmale
    hair_color: Optional[str] = None
    approximate_age: Optional[int] = None

    # Emotionale Profile
    dominant_emotions: Optional[List[str]] = None
    emotion_frequencies: Optional[Dict[str, int]] = None

    # Bekleidungsanalyse
    clothing_styles: Optional[List[str]] = None
    typical_clothing: Optional[List[str]] = None

    # Restraint/BDSM-Profile
    restraint_types: Optional[List[str]] = None
    bondage_styles: Optional[List[str]] = None
    shibari_detected: bool = False

    # Medien-Auftritte
    total_appearances: int = 0
    media_files: Optional[List[str]] = None
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    # Re-ID Daten
    face_embeddings: Optional[List[List[float]]] = None
    face_similarity_group: Optional[str] = None


class ComplexPersonQuery(BaseModel):
    """Erweiterte Suchanfrage für Personen-Dossiers."""

    # Erscheinungsmerkmale
    hair_color: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None

    # Emotionale Filter
    emotions: Optional[List[str]] = None
    dominant_emotion: Optional[str] = None

    # Bekleidungsfilter
    clothing_styles: Optional[List[str]] = None
    clothing_items: Optional[List[str]] = None

    # BDSM/Restraint-Filter
    restraint_types: Optional[List[str]] = None
    bondage_styles: Optional[List[str]] = None
    include_shibari: Optional[bool] = None

    # NSFW-Filter
    nsfw_content: Optional[bool] = None
    content_rating: Optional[str] = None

    # Zeitraum
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Ergebnisse
    limit: int = 50
    min_appearances: int = 1
    min_confidence: float = 0.5


class InsightsDossierService:
    """
    Insights-basierter Dossier Service mit erweiterten Suchfunktionen.

    Ermöglicht komplexe Abfragen wie:
    - "Alle blonden Frauen in Shibari-Fesselungen"
    - "Glückliche Personen in roter Kleidung"
    - "Personen mit mehr als 5 Auftritten im letzten Monat"
    """

    def __init__(self):
        self.person_profiles: Dict[str, PersonProfile] = {}

    async def build_person_profile(self, person_id: str) -> PersonProfile:
        """
        Erstellt vollständiges Personen-Profil aus allen Insights.
        """

        # Alle Insights für diese Person sammeln
        person_insights = insights_service.search_insights(
            search_text=person_id,
            limit=1000
        )

        if not person_insights:
            raise HTTPException(status_code=404, detail=f"Keine Insights für Person {person_id}")

        # Profil-Daten aggregieren
        profile_data = self._aggregate_person_data(person_insights)

        # Vollständiges Profil erstellen
        profile = PersonProfile(
            person_id=person_id,
            display_name=profile_data.get("display_name", f"Person_{person_id[:8]}"),
            confidence_score=profile_data.get("avg_confidence", 0.0),

            # Erscheinung
            hair_color=self._extract_hair_color(profile_data),
            approximate_age=profile_data.get("estimated_age"),

            # Emotionen
            dominant_emotions=self._get_dominant_emotions(profile_data),
            emotion_frequencies=profile_data.get("emotion_counts", {}),

            # Kleidung
            clothing_styles=profile_data.get("clothing_styles", []),
            typical_clothing=profile_data.get("typical_clothing", []),

            # Restraints
            restraint_types=profile_data.get("restraint_types", []),
            bondage_styles=profile_data.get("bondage_styles", []),
            shibari_detected=self._check_shibari_presence(profile_data),

            # Statistiken
            total_appearances=len(person_insights),
            media_files=list(set([insight["media_filename"] for insight in person_insights])),
            first_seen=min([datetime.fromisoformat(insight["created_at"]) for insight in person_insights]),
            last_seen=max([datetime.fromisoformat(insight["created_at"]) for insight in person_insights]),

            # Re-ID
            face_embeddings=self._extract_face_embeddings(profile_data),
            face_similarity_group=self._determine_similarity_group(person_id)
        )

        # Cache für Performance
        self.person_profiles[person_id] = profile

        return profile

    def _aggregate_person_data(self, insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregiert alle Insight-Daten für eine Person."""

        aggregated: Dict[str, Any] = {
            "emotion_counts": defaultdict(int),
            "clothing_styles": [],
            "typical_clothing": [],
            "restraint_types": [],
            "bondage_styles": [],
            "nsfw_detections": [],
            "confidence_scores": [],
            "face_embeddings": [],
            "hair_colors": [],
            "ages": []
        }

        for insight in insights:
            insight_type = insight["insight_type"]
            raw_data = insight.get("raw_data", {})
            confidence = insight.get("confidence", 0.0)

            aggregated["confidence_scores"].append(confidence)

            # Person Detection Insights
            if insight_type == "person_detection":
                emotions = raw_data.get("emotions", [])
                for emotion in emotions:
                    aggregated["emotion_counts"][emotion] += 1

                # Haar-/Altersschätzung aus verschiedenen Quellen
                if "hair_color" in raw_data:
                    aggregated["hair_colors"].append(raw_data["hair_color"])
                if "age_estimate" in raw_data:
                    aggregated["ages"].append(raw_data["age_estimate"])

                # Face Embeddings für Re-ID
                if "embedding" in raw_data:
                    aggregated["face_embeddings"].append(raw_data["embedding"])

            # Clothing Analysis Insights
            elif insight_type == "clothing_analysis":
                clothing_items = raw_data.get("detected_clothing", [])
                aggregated["typical_clothing"].extend(clothing_items)

                style = raw_data.get("overall_style")
                if style:
                    aggregated["clothing_styles"].append(style)

            # Restraint Detection Insights
            elif insight_type == "restraint_detection":
                restraints = raw_data.get("detected_restraints", [])
                aggregated["restraint_types"].extend(restraints)

                # Spezielle Bondage-Styles erkennen
                bondage_styles = raw_data.get("bondage_styles", [])
                aggregated["bondage_styles"].extend(bondage_styles)

            # NSFW Detection Insights
            elif insight_type == "nsfw_detection":
                if raw_data.get("is_nsfw"):
                    aggregated["nsfw_detections"].append(raw_data)

        # Durchschnittswerte berechnen
        confidence_scores = aggregated["confidence_scores"]
        aggregated["avg_confidence"] = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        ages = aggregated["ages"]
        aggregated["estimated_age"] = int(sum(ages) / len(ages)) if ages else None

        # Häufigste Werte bestimmen
        hair_colors = aggregated["hair_colors"]
        aggregated["most_common_hair"] = max(set(hair_colors), key=hair_colors.count) if hair_colors else None

        return aggregated

    def _extract_hair_color(self, profile_data: Dict[str, Any]) -> Optional[str]:
        """Extrahiert dominante Haarfarbe."""
        return profile_data.get("most_common_hair")

    def _get_dominant_emotions(self, profile_data: Dict[str, Any]) -> List[str]:
        """Gibt die 3 häufigsten Emotionen zurück."""
        emotion_counts = profile_data.get("emotion_counts", {})
        sorted_emotions = sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)
        return [emotion for emotion, _ in sorted_emotions[:3]]

    def _check_shibari_presence(self, profile_data: Dict[str, Any]) -> bool:
        """Prüft ob Shibari-Fesselungen erkannt wurden."""
        restraint_types = profile_data.get("restraint_types", [])
        bondage_styles = profile_data.get("bondage_styles", [])

        shibari_keywords = ["shibari", "rope_bondage", "japanese_bondage", "kinbaku"]

        all_terms = restraint_types + bondage_styles
        return any(keyword in str(all_terms).lower() for keyword in shibari_keywords)

    def _extract_face_embeddings(self, profile_data: Dict[str, Any]) -> List[List[float]]:
        """Extrahiert Face-Embeddings für Re-ID."""
        return profile_data.get("face_embeddings", [])

    def _determine_similarity_group(self, person_id: str) -> Optional[str]:
        """Bestimmt Ähnlichkeitsgruppe für Re-ID."""
        # Vereinfachte Implementierung - in Realität würde hier
        # Face-Embedding-Vergleich mit anderen Personen stattfinden
        return f"group_{person_id[:4]}"

    async def complex_person_search(self, query: ComplexPersonQuery) -> List[PersonProfile]:
        """
        Führt komplexe Personen-Suche durch.

        Beispiele:
        - Blondine + Shibari: hair_color="blonde", include_shibari=True
        - Glückliche Personen in rot: emotions=["happy"], clothing_items=["red"]
        """

        print(f"🔍 Starting complex search with query: {query}")

        # Basis-Insights sammeln
        insights_query_parts = []

        # Suchterme für Volltext-Suche aufbauen
        search_terms = []

        if query.hair_color:
            search_terms.append(query.hair_color)

        if query.emotions:
            search_terms.extend(query.emotions)

        if query.clothing_items:
            search_terms.extend(query.clothing_items)

        if query.include_shibari:
            search_terms.extend(["shibari", "rope", "bondage"])

        if query.restraint_types:
            search_terms.extend(query.restraint_types)

        # Insights-Suche durchführen
        base_search = " ".join(search_terms) if search_terms else None
        print(f"🔍 Search terms: {search_terms} -> base_search: {base_search}")

        relevant_insights = insights_service.search_insights(
            search_text=base_search,
            insight_types=[t for t in ["person_detection", "clothing_analysis", "restraint_detection"] if self._type_matches_query(t, query)],
            start_date=query.start_date,
            end_date=query.end_date,
            limit=query.limit * 10  # Mehr sammeln für Filterung
        )

        print(f"🔍 Found {len(relevant_insights)} relevant insights")

        # Personen-IDs extrahieren und Profile erstellen
        person_ids = set()
        for insight in relevant_insights:
            # Vereinfachte Person-ID-Extraktion aus Job-ID oder Media-ID
            person_id = self._extract_person_id_from_insight(insight)
            if person_id:
                person_ids.add(person_id)

        print(f"🔍 Extracted person IDs: {person_ids}")

        # Profile erstellen und filtern
        matching_profiles = []

        for person_id in person_ids:
            try:
                profile = await self.build_person_profile(person_id)
                print(f"🔍 Built profile for {person_id}: {profile.display_name}")

                # Detaillierte Filter anwenden
                if self._profile_matches_query(profile, query):
                    matching_profiles.append(profile)
                    print(f"✅ Profile {person_id} matches query!")
                else:
                    print(f"❌ Profile {person_id} does not match query")

            except Exception as e:
                print(f"Fehler bei Profil-Erstellung für {person_id}: {e}")
                continue

        print(f"🔍 Final matching profiles: {len(matching_profiles)}")

        # Nach Confidence sortieren
        matching_profiles.sort(key=lambda p: p.confidence_score, reverse=True)

        return matching_profiles[:query.limit]

    def _type_matches_query(self, insight_type: str, query: ComplexPersonQuery) -> bool:
        """Prüft ob Insight-Typ zur Query passt."""
        # Für komplexe Queries brauchen wir alle relevanten Typen
        return True  # Vereinfacht: Alle Insight-Typen akzeptieren

    def _extract_person_id_from_insight(self, insight: Dict[str, Any]) -> Optional[str]:
        """Extrahiert Person-ID aus Insight."""
        # Verschiedene Strategien für Person-ID-Extraktion
        raw_data = insight.get("raw_data", {})

        # Direkte Person-ID
        if "person_id" in raw_data:
            return raw_data["person_id"]

        # Face-ID als Person-ID
        if "face_id" in raw_data:
            return raw_data["face_id"]

        # Job-ID als Fallback
        return insight.get("job_id")

    def _profile_matches_query(self, profile: PersonProfile, query: ComplexPersonQuery) -> bool:
        """Prüft ob Profil der komplexen Query entspricht."""

        # Haarfarbe-Filter
        if query.hair_color and profile.hair_color != query.hair_color.lower():
            return False

        # Alters-Filter
        if query.age_min and (not profile.approximate_age or profile.approximate_age < query.age_min):
            return False
        if query.age_max and (not profile.approximate_age or profile.approximate_age > query.age_max):
            return False

        # Emotions-Filter
        if query.emotions:
            if not profile.dominant_emotions:
                return False
            if not any(emotion.lower() in [e.lower() for e in profile.dominant_emotions] for emotion in query.emotions):
                return False

        # Kleidungs-Filter
        if query.clothing_items:
            if not profile.typical_clothing:
                return False
            if not any(item.lower() in [c.lower() for c in profile.typical_clothing] for item in query.clothing_items):
                return False

        # Shibari-Filter (DAS WICHTIGE!)
        if query.include_shibari and not profile.shibari_detected:
            return False

        # Restraint-Filter
        if query.restraint_types:
            if not profile.restraint_types:
                return False
            if not any(rtype.lower() in [r.lower() for r in profile.restraint_types] for rtype in query.restraint_types):
                return False

        # Mindest-Auftritte
        if profile.total_appearances < query.min_appearances:
            return False

        # Mindest-Confidence
        if profile.confidence_score < query.min_confidence:
            return False

        return True


# Globaler Service
insights_dossier_service = InsightsDossierService()

app = FastAPI(
    title="🔍 Insights-basierter Personen-Dossier Service",
    description="Erweiterte Personen-Analyse mit komplexen Suchabfragen",
    version="1.0.0"
)


@app.get("/person/{person_id}/profile", response_model=PersonProfile)
async def get_person_profile(person_id: str):
    """Gibt vollständiges Personen-Profil zurück."""
    return await insights_dossier_service.build_person_profile(person_id)


@app.post("/search/complex")
async def complex_person_search(query: ComplexPersonQuery):
    """
    Komplexe Personen-Suche.

    Beispiele:
    - Blondine + Shibari: {"hair_color": "blonde", "include_shibari": true}
    - Glückliche Personen in rot: {"emotions": ["happy"], "clothing_items": ["red"]}
    """
    return await insights_dossier_service.complex_person_search(query)


@app.get("/examples/blonde-shibari")
async def search_blonde_shibari():
    """
    🎯 BEISPIEL: Alle blonden Frauen in Shibari-Fesselungen.

    Dies ist genau das Feature, das Sie angefordert haben!
    """
    query = ComplexPersonQuery(
        hair_color="blonde",
        include_shibari=True,
        min_appearances=1,
        limit=20
    )

    results = await insights_dossier_service.complex_person_search(query)

    return {
        "query_description": "Blondine + Shibari",
        "total_matches": len(results),
        "persons": results
    }


@app.get("/health")
async def health_check():
    """Health Check."""
    return {"status": "healthy", "service": "insights_dossier"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)

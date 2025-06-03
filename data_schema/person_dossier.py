import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class EmotionType(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    DISGUSTED = "disgusted"
    NEUTRAL = "neutral"
    PAIN = "pain"
    PLEASURE = "pleasure"


class RestraintType(str, Enum):
    ROPE = "rope"
    CHAINS = "chains"
    HANDCUFFS = "handcuffs"
    TAPE = "tape"
    OTHER = "other"


class MediaAppearance(BaseModel):
    media_id: str
    job_id: str
    source_type: str
    timestamp: datetime
    duration: Optional[float] = None  # Für Videos
    frame_number: Optional[int] = None  # Für Videos
    confidence: float
    emotions: List[Dict[str, float]] = []  # Liste von Emotionen mit Konfidenzwerten
    restraints: List[Dict[str, float]] = []  # Liste von Restraints mit Konfidenzwerten
    context: Optional[str] = None  # Zusätzlicher Kontext
    scene_description: Optional[str] = None  # Beschreibung der Szene


class FaceInstance(BaseModel):
    face_id: str
    job_id: str
    media_id: str
    source_type: str
    timestamp: datetime
    bbox: Dict[str, int]
    confidence: float
    embedding: List[float]
    image_url: Optional[str] = None
    emotions: List[Dict[str, float]] = []  # Liste von Emotionen mit Konfidenzwerten
    restraints: List[Dict[str, float]] = []  # Liste von Restraints mit Konfidenzwerten


class PersonDossier(BaseModel):
    dossier_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    temporary_id: str
    display_name: Optional[str] = None
    notes: Optional[str] = None
    face_instances: List[FaceInstance] = []
    media_appearances: List[MediaAppearance] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = {}

    # Statistik-Felder
    emotion_stats: Dict[str, int] = Field(default_factory=dict)
    restraint_stats: Dict[str, int] = Field(default_factory=dict)
    total_appearances: int = 0

    def add_face_instance(self, face_instance: FaceInstance):
        self.face_instances.append(face_instance)
        self._update_statistics()
        self.updated_at = datetime.utcnow()

    def add_media_appearance(self, appearance: MediaAppearance):
        self.media_appearances.append(appearance)
        self._update_statistics()
        self.updated_at = datetime.utcnow()

    def _update_statistics(self):
        """
        Aktualisiert alle Statistiken mit Event-Driven Architecture.
        """
        try:
            # Phase 1: Basis-Statistiken berechnen
            self._calculate_basic_statistics()

            # Phase 2: Zeitbasierte Statistiken
            self._calculate_temporal_statistics()

            # Phase 3: Erkennungs-Statistiken
            self._calculate_detection_statistics()

            # Phase 4: Qualitäts-Metriken
            self._calculate_quality_metrics()

            # Phase 5: Finale Aggregation
            self._finalize_statistics_update()

        except Exception as e:
            # Fallback auf leere Statistiken
            self._initialize_empty_statistics()
            raise

    def _calculate_basic_statistics(self) -> None:
        """Berechnet grundlegende Auftrittshäufigkeiten."""
        self.emotion_stats = {}
        self.restraint_stats = {}
        self.total_appearances = len(self.media_appearances)
        self.emotion_stats["total_appearances"] = self.total_appearances
        self.restraint_stats["total_appearances"] = self.total_appearances

    def _calculate_temporal_statistics(self) -> None:
        """Berechnet zeitbasierte Statistiken."""
        if not self.media_appearances:
            self._set_empty_temporal_stats()
            return

        timestamps = [app.timestamp for app in self.media_appearances if app.timestamp]

        if timestamps:
            self.emotion_stats["first_seen"] = min(timestamps)
            self.emotion_stats["last_seen"] = max(timestamps)
            self.emotion_stats["active_period_days"] = self._calculate_active_period(timestamps)
            self.emotion_stats["appearance_frequency"] = self._calculate_appearance_frequency(timestamps)
            self.restraint_stats["first_seen"] = min(timestamps)
            self.restraint_stats["last_seen"] = max(timestamps)
            self.restraint_stats["active_period_days"] = self._calculate_active_period(timestamps)
            self.restraint_stats["appearance_frequency"] = self._calculate_appearance_frequency(timestamps)
        else:
            self._set_empty_temporal_stats()

    def _set_empty_temporal_stats(self) -> None:
        """Setzt leere zeitbasierte Statistiken."""
        # Phase 1: Emotion-Counts sammeln
        emotion_counts = self._collect_emotion_counts()

        # Phase 2: Restraint-Counts sammeln
        restraint_counts = self._collect_restraint_counts()

        # Phase 3: Statistiken finalisieren
        self._finalize_collected_stats(emotion_counts, restraint_counts)

    def _collect_emotion_counts(self) -> Dict[str, int]:
        """Sammelt Emotion-Counts aus allen Quellen."""
        emotion_counts = {}

        # Aus Face Instances sammeln
        self._process_face_emotions(emotion_counts)

        # Aus Media Appearances sammeln
        self._process_media_emotions(emotion_counts)

        return emotion_counts

    def _collect_restraint_counts(self) -> Dict[str, int]:
        """Sammelt Restraint-Counts aus allen Quellen."""
        restraint_counts = {}

        # Aus Face Instances sammeln
        self._process_face_restraints(restraint_counts)

        # Aus Media Appearances sammeln
        self._process_media_restraints(restraint_counts)

        return restraint_counts

    def _process_face_emotions(self, emotion_counts: Dict[str, int]) -> None:
        """Verarbeitet Emotionen aus Face Instances."""
        for face in self.face_instances:
            for emotion in face.emotions:
                for emotion_type, confidence in emotion.items():
                    if confidence > 0.5:
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1

    def _process_face_restraints(self, restraint_counts: Dict[str, int]) -> None:
        """Verarbeitet Restraints aus Face Instances."""
        for face in self.face_instances:
            for restraint in face.restraints:
                for restraint_type, confidence in restraint.items():
                    if confidence > 0.5:
                        restraint_counts[restraint_type] = restraint_counts.get(restraint_type, 0) + 1

    def _process_media_emotions(self, emotion_counts: Dict[str, int]) -> None:
        """Verarbeitet Emotionen aus Media Appearances."""
        for appearance in self.media_appearances:
            for emotion in appearance.emotions:
                for emotion_type, confidence in emotion.items():
                    if confidence > 0.5:
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1

    def _process_media_restraints(self, restraint_counts: Dict[str, int]) -> None:
        """Verarbeitet Restraints aus Media Appearances."""
        for appearance in self.media_appearances:
            for restraint in appearance.restraints:
                for restraint_type, confidence in restraint.items():
                    if confidence > 0.5:
                        restraint_counts[restraint_type] = restraint_counts.get(restraint_type, 0) + 1

    def _finalize_collected_stats(self, emotion_counts: Dict[str, int], restraint_counts: Dict[str, int]) -> None:
        """Finalisiert gesammelte Statistiken."""
        self.emotion_stats = emotion_counts
        self.restraint_stats = restraint_counts
        self.total_appearances = len(self.media_appearances)

    def update_metadata(self, key: str, value: str):
        self.metadata[key] = value
        self.updated_at = datetime.utcnow()

    def update_display_name(self, name: str):
        self.display_name = name
        self.updated_at = datetime.utcnow()

    def update_notes(self, notes: str):
        self.notes = notes
        self.updated_at = datetime.utcnow()

    def get_emotion_summary(self) -> Dict[str, float]:
        """Gibt eine Zusammenfassung der Emotionen zurück"""
        total = sum(self.emotion_stats.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in self.emotion_stats.items()}

    def get_restraint_summary(self) -> Dict[str, float]:
        """Gibt eine Zusammenfassung der Restraints zurück"""
        total = sum(self.restraint_stats.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in self.restraint_stats.items()}

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from enum import Enum

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
        """Aktualisiert die Statistik-Felder"""
        # Emotionen zählen
        emotion_counts = {}
        restraint_counts = {}
        
        # Aus Face Instances
        for face in self.face_instances:
            for emotion in face.emotions:
                for emotion_type, confidence in emotion.items():
                    if confidence > 0.5:  # Nur signifikante Emotionen
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            
            for restraint in face.restraints:
                for restraint_type, confidence in restraint.items():
                    if confidence > 0.5:  # Nur signifikante Restraints
                        restraint_counts[restraint_type] = restraint_counts.get(restraint_type, 0) + 1
        
        # Aus Media Appearances
        for appearance in self.media_appearances:
            for emotion in appearance.emotions:
                for emotion_type, confidence in emotion.items():
                    if confidence > 0.5:
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
            
            for restraint in appearance.restraints:
                for restraint_type, confidence in restraint.items():
                    if confidence > 0.5:
                        restraint_counts[restraint_type] = restraint_counts.get(restraint_type, 0) + 1
        
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
        return {k: v/total for k, v in self.emotion_stats.items()}
    
    def get_restraint_summary(self) -> Dict[str, float]:
        """Gibt eine Zusammenfassung der Restraints zurück"""
        total = sum(self.restraint_stats.values())
        if total == 0:
            return {}
        return {k: v/total for k, v in self.restraint_stats.items()} 
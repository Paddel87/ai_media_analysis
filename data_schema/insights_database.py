"""
Einfache durchsuchbare Erkenntnisse-Datenbank für AI Media Analysis.
Speichert alle Analyseergebnisse in einer einheitlichen, durchsuchbaren Struktur.
"""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InsightType(str, Enum):
    """Kategorien der Analyseergebnisse."""
    PERSON_DETECTION = "person_detection"
    EMOTION_ANALYSIS = "emotion_analysis"
    RESTRAINT_DETECTION = "restraint_detection"
    CLOTHING_ANALYSIS = "clothing_analysis"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    VIDEO_CONTEXT = "video_context"
    NSFW_DETECTION = "nsfw_detection"
    OBJECT_DETECTION = "object_detection"
    OCR_TEXT = "ocr_text"
    POSE_ESTIMATION = "pose_estimation"


class InsightEntry(BaseModel):
    """Einzelner Erkenntnisse-Eintrag in der Datenbank."""

    # Basis-Identifikation
    insight_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str
    media_id: str
    media_type: str  # "video", "image", "audio"
    media_filename: str

    # Kategorisierung
    insight_type: InsightType
    category: str  # Zusätzliche Unterkategorie
    tags: List[str] = Field(default_factory=list)  # Meta-Tags für Suche

    # Zeitstempel
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    media_timestamp: Optional[float] = None  # Position im Video/Audio

    # Kerninhalt
    title: str  # Kurze Beschreibung
    description: str  # Detaillierte Beschreibung
    confidence: float = Field(ge=0.0, le=1.0)

    # Strukturierte Daten
    raw_data: Dict[str, Any] = Field(default_factory=dict)  # Original-Analysedaten
    metadata: Dict[str, str] = Field(default_factory=dict)  # Zusätzliche Metadaten

    # Suchhilfen
    searchable_text: str = ""  # Volltext für Suche
    keywords: List[str] = Field(default_factory=list)  # Schlüsselwörter

    def __post_init__(self):
        """Automatische Generierung der Suchhilfen."""
        if not self.searchable_text:
            self.searchable_text = self._generate_searchable_text()
        if not self.keywords:
            self.keywords = self._extract_keywords()

    def _generate_searchable_text(self) -> str:
        """Generiert durchsuchbaren Text aus allen Feldern."""
        parts = [
            self.title,
            self.description,
            self.media_filename,
            self.category,
            " ".join(self.tags),
            " ".join(self.keywords),
        ]

        # Raw data einbeziehen wenn möglich
        for value in self.raw_data.values():
            if isinstance(value, str):
                parts.append(value)

        return " ".join(filter(None, parts)).lower()

    def _extract_keywords(self) -> List[str]:
        """Extrahiert Schlüsselwörter aus dem Inhalt."""
        keywords: List[str] = []

        # Aus Titel und Beschreibung
        text = f"{self.title} {self.description}".lower()

        # Einfache Keyword-Extraktion
        words = text.split()
        keywords.extend([word for word in words if len(word) > 3])

        # Aus Tags
        keywords.extend(self.tags)

        # Duplikate entfernen
        return list(set(keywords))


class InsightQuery(BaseModel):
    """Suchanfrage für die Erkenntnisse-Datenbank."""

    # Volltext-Suche
    search_text: Optional[str] = None

    # Filter
    insight_types: Optional[List[InsightType]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    # Zeitraum
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    # Medien-Filter
    media_types: Optional[List[str]] = None
    job_ids: Optional[List[str]] = None

    # Qualitäts-Filter
    min_confidence: Optional[float] = None

    # Paginierung
    limit: int = 50
    offset: int = 0

    # Sortierung
    sort_by: str = "created_at"
    sort_order: str = "DESC"  # ASC oder DESC


class InsightsDatabase:
    """Einfache SQLite-basierte Erkenntnisse-Datenbank mit Volltext-Suche."""

    def __init__(self, db_path: str = "data/insights.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialisiert die SQLite-Datenbank mit FTS5-Unterstützung."""
        with sqlite3.connect(self.db_path) as conn:
            # Haupt-Tabelle für Erkenntnisse
            conn.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    insight_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    media_id TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    media_filename TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    media_timestamp REAL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    raw_data TEXT,  -- JSON
                    metadata TEXT,  -- JSON
                    searchable_text TEXT NOT NULL,
                    keywords TEXT  -- JSON array
                )
            """)

            # Volltext-Suche-Index mit FTS5
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS insights_fts USING fts5(
                    insight_id,
                    title,
                    description,
                    searchable_text,
                    keywords,
                    content='insights',
                    content_rowid='rowid'
                )
            """)

            # Trigger für automatische FTS-Updates
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS insights_fts_insert AFTER INSERT ON insights BEGIN
                    INSERT INTO insights_fts(
                        insight_id, title, description, searchable_text, keywords
                    ) VALUES (
                        new.insight_id, new.title, new.description,
                        new.searchable_text, new.keywords
                    );
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS insights_fts_update AFTER UPDATE ON insights BEGIN
                    UPDATE insights_fts SET
                        title = new.title,
                        description = new.description,
                        searchable_text = new.searchable_text,
                        keywords = new.keywords
                    WHERE insight_id = new.insight_id;
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS insights_fts_delete AFTER DELETE ON insights BEGIN
                    DELETE FROM insights_fts WHERE insight_id = old.insight_id;
                END
            """)

            # Indizes für bessere Performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON insights(job_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_media_id ON insights(media_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_insight_type ON insights(insight_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON insights(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON insights(confidence)")

            conn.commit()

    def add_insight(self, insight: InsightEntry) -> str:
        """Fügt eine neue Erkenntnis zur Datenbank hinzu."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO insights (
                    insight_id, job_id, media_id, media_type, media_filename,
                    insight_type, category, tags, created_at, media_timestamp,
                    title, description, confidence, raw_data, metadata,
                    searchable_text, keywords
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                insight.insight_id,
                insight.job_id,
                insight.media_id,
                insight.media_type,
                insight.media_filename,
                insight.insight_type.value,
                insight.category,
                json.dumps(insight.tags),
                insight.created_at.isoformat(),
                insight.media_timestamp,
                insight.title,
                insight.description,
                insight.confidence,
                json.dumps(insight.raw_data),
                json.dumps(insight.metadata),
                insight.searchable_text,
                json.dumps(insight.keywords)
            ))
            conn.commit()

        return insight.insight_id

    def search(self, query: InsightQuery) -> List[Dict[str, Any]]:
        """Durchsucht die Erkenntnisse-Datenbank."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Basis-Query
            sql_parts: List[str] = ["SELECT * FROM insights WHERE 1=1"]
            params: List[Any] = []

            # Volltext-Suche
            if query.search_text:
                sql_parts.append("""
                    AND insight_id IN (
                        SELECT insight_id FROM insights_fts
                        WHERE insights_fts MATCH ?
                    )
                """)
                params.append(query.search_text)

            # Filter
            if query.insight_types:
                placeholders = ",".join("?" * len(query.insight_types))
                sql_parts.append(f"AND insight_type IN ({placeholders})")
                params.extend([t.value for t in query.insight_types])

            if query.categories:
                placeholders = ",".join("?" * len(query.categories))
                sql_parts.append(f"AND category IN ({placeholders})")
                params.extend(query.categories)

            if query.start_date:
                sql_parts.append("AND created_at >= ?")
                params.append(query.start_date.isoformat())

            if query.end_date:
                sql_parts.append("AND created_at <= ?")
                params.append(query.end_date.isoformat())

            if query.media_types:
                placeholders = ",".join("?" * len(query.media_types))
                sql_parts.append(f"AND media_type IN ({placeholders})")
                params.extend(query.media_types)

            if query.job_ids:
                placeholders = ",".join("?" * len(query.job_ids))
                sql_parts.append(f"AND job_id IN ({placeholders})")
                params.extend(query.job_ids)

            if query.min_confidence:
                sql_parts.append("AND confidence >= ?")
                params.append(query.min_confidence)

            # Tags-Suche (JSON-basiert)
            if query.tags:
                for tag in query.tags:
                    sql_parts.append("AND tags LIKE ?")
                    params.append(f'%"{tag}"%')

            # Sortierung
            sql_parts.append(f"ORDER BY {query.sort_by} {query.sort_order}")

            # Paginierung
            sql_parts.append("LIMIT ? OFFSET ?")
            params.extend([query.limit, query.offset])

            # Query ausführen
            sql = " ".join(sql_parts)
            cursor = conn.execute(sql, params)

            # Ergebnisse verarbeiten
            results: List[Dict[str, Any]] = []
            for row in cursor.fetchall():
                result: Dict[str, Any] = dict(row)
                # JSON-Felder deserialisieren
                result['tags'] = json.loads(result['tags'] or '[]')
                result['raw_data'] = json.loads(result['raw_data'] or '{}')
                result['metadata'] = json.loads(result['metadata'] or '{}')
                result['keywords'] = json.loads(result['keywords'] or '[]')
                results.append(result)

            return results

    def get_insights_summary(self) -> Dict[str, Any]:
        """Gibt eine Zusammenfassung der gespeicherten Erkenntnisse zurück."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Gesamt-Statistiken
            total = conn.execute("SELECT COUNT(*) as count FROM insights").fetchone()['count']

            # Nach Typ
            by_type = {}
            cursor = conn.execute("""
                SELECT insight_type, COUNT(*) as count
                FROM insights
                GROUP BY insight_type
            """)
            for row in cursor:
                by_type[row['insight_type']] = row['count']

            # Nach Medientyp
            by_media = {}
            cursor = conn.execute("""
                SELECT media_type, COUNT(*) as count
                FROM insights
                GROUP BY media_type
            """)
            for row in cursor:
                by_media[row['media_type']] = row['count']

            # Neueste Erkenntnisse
            latest = conn.execute("""
                SELECT created_at
                FROM insights
                ORDER BY created_at DESC
                LIMIT 1
            """).fetchone()

            return {
                "total_insights": total,
                "by_insight_type": by_type,
                "by_media_type": by_media,
                "latest_insight": latest['created_at'] if latest else None
            }

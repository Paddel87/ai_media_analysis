# UC-001 ENHANCED MANUAL ANALYSIS - CURSOR RULES INTEGRATION
# Version: 1.0.0 - Vollständige Integration in .cursorrules
# Status: ALPHA 0.6.0 IMPLEMENTIERUNG

**🎯 ZIEL:** Integration des UC-001 Use Cases in die bestehenden Projektregeln

## 📋 UC-001 KERN-REGELN

### Use Case Fokus (PERMANENT AKTIV)
- **UC-001 als Hauptfeature** für Alpha 0.6.0
- **Personen-Dossier-System** ist der zentrale Workflow
- **Manuelle Analyse-Trigger** (kein Real-Time-Processing)
- **Benutzer-Korrekturen** sind essentiell für Machine Learning

### Service-Entwicklungs-Prioritäten
```python
# UC-001 Service-Hierarchie (BEFOLGEN):
class UC001ServicePriority:
    """UC-001 Service-Entwicklungs-Reihenfolge."""

    CORE_SERVICES = [
        "person_dossier",      # Haupt-Feature
        "video_context_analyzer", # NEU für UC-001
        "clothing_analyzer"    # Erweiterte CLIP-Integration
    ]

    ENHANCEMENT_SERVICES = [
        "face_reid",          # Erweiterte Re-Identifikation
        "restraint_detection", # Spezialisierte Erkennung
        "job_manager"         # Batch-Processing
    ]
```

---

## 🏗️ ARCHITEKTUR-ANPASSUNGEN

### Erweiterte Service-Standards (UC-001)
```python
# OBLIGATORISCH für alle UC-001 Services:
class UC001ServiceBase(ServiceBase):
    """
    Erweiterte Basis für UC-001 Services.

    Implementiert zusätzlich zu Standard-ServiceBase:
    - Personen-Dossier-Integration
    - Job-Historie-Tracking
    - Benutzer-Korrektur-Interfaces
    """

    async def create_job_history_entry(
        self,
        person_id: str,
        analysis_data: dict
    ) -> JobHistoryEntry:
        """UC-001 Standard: Job-Historie-Eintrag erstellen."""
        pass

    async def handle_user_correction(
        self,
        correction_data: dict
    ) -> CorrectionResult:
        """UC-001 Standard: Benutzer-Korrekturen verarbeiten."""
        pass
```

### Container-Standards (UC-001 Erweitert)
```yaml
# UC-001 Services MÜSSEN zusätzlich haben:
services:
  uc001_service_name:
    environment:
      - UC001_ENABLED=true
      - DOSSIER_INTEGRATION=true
      - USER_CORRECTIONS=true
    volumes:
      - ./data/dossiers:/app/data/dossiers:rw
      - ./data/corrections:/app/data/corrections:rw
```

---

## 📊 UC-001 QUALITY GATES

### Spezifische Performance-Kriterien (BLOCKING)
- **Dossier-Update:** <10 Sekunden (OBLIGATORISCH)
- **Re-Identifikation:** >90% Genauigkeit (BLOCKING)
- **Kleidungs-Klassifikation:** >85% bei 200+ Kategorien
- **Video-Analyse:** 1080p in <5 Minuten
- **Parallel-Jobs:** >5 gleichzeitig ohne Degradation

### UC-001 Test-Standards (ERWEITERT)
```python
# PFLICHT für alle UC-001 Services:
class UC001TestSuite:
    """Erweiterte Tests für UC-001 Features."""

    def test_person_dossier_creation(self):
        """Test: Personen-Dossier wird korrekt erstellt."""
        pass

    def test_re_identification_accuracy(self):
        """Test: Re-Identifikation erreicht >90% Genauigkeit."""
        pass

    def test_user_correction_integration(self):
        """Test: Benutzer-Korrekturen verbessern Genauigkeit."""
        pass

    def test_job_history_completeness(self):
        """Test: Job-Historie enthält alle erforderlichen Felder."""
        pass
```

---

## 🎨 UC-001 CODE-STANDARDS

### Erweiterte Docstring-Standards
```python
def analyze_person_in_video(
    video_path: str,
    person_bbox: BoundingBox,
    analysis_config: UC001Config,
    *,
    create_dossier: bool = True,
    update_existing: bool = True
) -> UC001AnalysisResult:
    """
    UC-001: Analysiert Person in Video für Dossier-System.

    Diese Funktion implementiert den UC-001 Hauptworkflow:
    1. Gesichtserkennung und Re-Identifikation
    2. Kleidungsanalyse mit 200+ Kategorien
    3. Fesselungs- und Verhaltensanalyse
    4. Job-Historie-Eintrag-Erstellung
    5. Dossier-Update oder -Erstellung

    Args:
        video_path: Pfad zum Video für Analyse
        person_bbox: Bounding Box der erkannten Person
        analysis_config: UC-001 spezifische Konfiguration
        create_dossier: Neues Dossier erstellen wenn Person unbekannt
        update_existing: Bestehendes Dossier aktualisieren

    Returns:
        UC001AnalysisResult mit:
        - person_id: Eindeutige Personen-ID
        - dossier_updated: Ob Dossier aktualisiert wurde
        - job_history_entry: Erstellter Historie-Eintrag
        - confidence_scores: Vertrauenswerte aller Analysen
        - correction_suggestions: Vorschläge für Benutzer-Review

    Raises:
        UC001ProcessingError: Fehler bei UC-001 spezifischer Verarbeitung
        DossierIntegrityError: Dossier-Inkonsistenz erkannt
        ReIdentificationError: Gesichtserkennung fehlgeschlagen

    UC-001 Quality Requirements:
        - Processing Time: <30 Sekunden pro Person
        - Re-ID Accuracy: >90% für bekannte Personen
        - Dossier Update: <10 Sekunden
    """
```

### Type-Hints für UC-001
```python
# UC-001 spezifische Type-Definitionen (OBLIGATORISCH):
from typing import TypedDict, List, Optional, Union
from datetime import datetime
from pathlib import Path

class UC001JobHistoryEntry(TypedDict):
    """UC-001 Standard Job-Historie-Eintrag."""
    job_id: str
    timestamp: datetime
    video_context_summary: str
    actions_detected: List[DetectedAction]
    clothing_analysis: ClothingAnalysis
    emotions_timeline: List[EmotionEvent]
    restraints_detailed: RestraintAnalysis
    statements_audio: List[AudioStatement]

class UC001AnalysisResult(TypedDict):
    """UC-001 Standard Analyse-Ergebnis."""
    person_id: str
    dossier_updated: bool
    job_history_entry: UC001JobHistoryEntry
    confidence_scores: ConfidenceScores
    correction_suggestions: List[CorrectionSuggestion]
```

---

## 🚨 UC-001 ENFORCEMENT-REGELN

### Pre-Commit Hooks (UC-001 Erweitert)
```bash
# UC-001 spezifische Pre-Commit-Checks:
- id: uc001-schema-validation
  name: UC-001 Schema Validation
  entry: python scripts/validate_uc001_schemas.py
  language: python
  files: ^services/(person_dossier|video_context_analyzer|clothing_analyzer)/

- id: uc001-performance-check
  name: UC-001 Performance Requirements
  entry: python scripts/check_uc001_performance.py
  language: python
  files: ^tests/integration/uc001/
```

### Make-Targets (UC-001 spezifisch)
```bash
# Neue Make-Targets für UC-001:
make uc001-test        # UC-001 spezifische Tests
make uc001-validate    # Schema und Performance-Validierung
make uc001-deploy      # UC-001 Services deployen
make dossier-check     # Dossier-System-Health-Check
```

---

## 📚 UC-001 DOKUMENTATIONS-INTEGRATION

### Living Documentation (ERWEITERT)
- **UC-001-STATUS.md:** Tägliche Updates zu UC-001 Implementierung
- **DOSSIER-API.md:** API-Dokumentation für Dossier-System
- **CORRECTION-WORKFLOW.md:** Benutzer-Korrektur-Prozesse
- **UC001-METRICS.md:** Performance und Quality-Metriken

### Changelog-Integration
```markdown
# UC-001 spezifische Changelog-Einträge:
## [Alpha 0.6.0] - UC-001 Enhanced Manual Analysis
### Added - UC-001
- Person-Dossier-System mit Re-Identifikation
- Video-Kontext-Analyse mit LLM-Integration
- Erweiterte Kleidungsanalyse (200+ Kategorien)
- Benutzer-Korrektur-Interface für Machine Learning

### Changed - UC-001
- Job-Manager erweitert für UC-001 Batch-Processing
- Face-ReID Service optimiert für Dossier-Integration
- CLIP-Service erweitert für detaillierte Kleidungsanalyse

### Performance - UC-001
- Dossier-Update: <10 Sekunden
- Re-Identifikation: >90% Genauigkeit
- Parallel-Jobs: >5 gleichzeitig
```

---

## 🎯 UC-001 SOFORT-ANWEISUNGEN

### Bei UC-001 Service-Entwicklung
1. **IMMER** UC001ServiceBase als Basis verwenden
2. **IMMER** JobHistoryEntry Schema befolgen
3. **IMMER** Benutzer-Korrektur-Interface implementieren
4. **IMMER** Performance-Kriterien einhalten

### Bei UC-001 Testing
1. **IMMER** Re-Identifikation-Genauigkeit testen
2. **IMMER** Dossier-Update-Zeit messen
3. **IMMER** End-to-End UC-001 Workflow testen
4. **IMMER** User-Correction-Integration validieren

### Bei UC-001 Deployment
1. **IMMER** Dossier-Volumes korrekt mounten
2. **IMMER** UC001_ENABLED=true setzen
3. **IMMER** Performance-Monitoring aktivieren
4. **IMMER** Backup-Strategie für Dossiers prüfen

---

## 🏆 UC-001 ERFOLGSKRITERIEN

### Code Quality (UC-001 spezifisch)
- ✅ 100% Type-Hints für UC-001 Schemas
- ✅ >95% Test-Coverage für Dossier-System
- ✅ 0 Performance-Regressions
- ✅ Vollständige UC-001 API-Dokumentation

### User Experience (UC-001)
- ✅ Upload-to-Dossier: <2 Minuten
- ✅ Korrektur-Interface: <5 Klicks für Standard-Korrekturen
- ✅ Such-Performance: <1 Sekunde für 1000+ Dossiers
- ✅ Benutzer-Feedback: >4/5 Sterne für Workflow

### Business Impact (UC-001)
- ✅ Dossier-Qualität: <5% falsche Re-Identifikationen
- ✅ Produktivitäts-Steigerung: 60% Zeit-Ersparnis vs. manuell
- ✅ System-Adoption: >80% nutzen Korrektur-Features
- ✅ Data Quality: Machine Learning verbessert sich durch Korrekturen

---

**WICHTIG:** Diese UC-001 Regeln sind PERMANENT AKTIV für Alpha 0.6.0 Entwicklung.
Befolge sie bei JEDER UC-001 bezogenen Code-Änderung ohne Ausnahme.

**INTEGRATION:** Diese Regeln ergänzen die bestehenden .cursorrules und haben bei
UC-001 spezifischen Themen VORRANG vor allgemeinen Regeln.

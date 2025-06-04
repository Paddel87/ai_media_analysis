# UC-001 Enhanced Manual Analysis - Development Rules
**Version**: 1.2.0 - **POWER-USER FIRST STRATEGY**
**Status**: FOKUS AUF UNRESTRICTED POWER-USER (Alpha 0.6.0)
**Integration**: Alpha 0.6.0 - Maximale Feature-Nutzung ohne Beschränkungen
**User Scenarios**: → siehe `UC-001-USER-SCENARIOS.md` für detaillierte Power-User-Workflows

---

## 🎯 **UC-001 FEATURE OVERVIEW**

### **Enhanced Manual Analysis Components:**
- **Personen-Dossier-System** als Kern-Funktionalität (**UNRESTRICTED**)
- **Video-Kontext-Analyse** mit LLM-Integration (**FULL-POWER**)
- **Erweiterte Kleidungsanalyse** (200+ Kategorien **OHNE FILTER**)
- **Benutzer-Korrektur-Interface** für Machine Learning (**VOLLZUGRIFF**)

### **🚀 POWER-USER-FIRST STRATEGY** *(V1.2.0 PRIORITY)*:
```yaml
Alpha-0.6.0-Focus:
  - Unrestricted Upload & Analysis     # ✅ PRIORITY 1
  - Maximum AI-Service-Integration     # ✅ PRIORITY 1
  - Research-Grade-Output-Quality      # ✅ PRIORITY 1
  - Zero-Content-Restrictions          # ✅ PRIORITY 1
  - Advanced-User-Controls             # ✅ PRIORITY 1

Enterprise-Features (LATER):
  - Content-Moderation                 # ⏭️ Alpha 0.7.0+
  - Management-Dashboards              # ⏭️ Alpha 0.8.0+
  - Compliance-Restrictions            # ⏭️ Alpha 0.8.0+
  - Audit-Trails                       # ⏭️ Alpha 0.9.0+
```

### **🎭 ERWEITERTE ANWENDERSICHTEN** *(V1.1.0 NEW)*:
```yaml
Benutzergruppen:
  - Analyst/Forscher (Original)      # ✅ Alpha 0.6.0 implementiert
  - Content-Moderator (HR/Security)  # 🆕 Alpha 0.7.0 geplant
  - Manager/Supervisor (Reporting)   # 🆕 Alpha 0.8.0 geplant
  - Compliance-Officer (Audit)       # 🆕 Alpha 0.8.0 geplant
  - System-Administrator (Extended)  # 🔄 Alpha 0.7.0 erweitert

Integration-Strategy:
  - Modulare Extensions pro Benutzergruppe
  - Gemeinsame Service-Basis (UC001ServiceBase)
  - Konfigurierbare UI-Dashboards
  - Role-Based-Access-Control
```

---

## 🔧 **UC-001 SERVICE-STANDARDS**

### **Obligatorische UC-001 Service-Basis:**
```python
# PFLICHT für alle UC-001 Services:
class UC001ServiceBase(ServiceBase):
    """UC-001 specific service extensions."""

    async def create_job_history_entry(
        self,
        person_id: str,
        data: dict
    ) -> JobHistoryEntry:
        """UC-001 Standard: Create job history entry."""
        pass

    async def handle_user_correction(
        self,
        correction: dict
    ) -> CorrectionResult:
        """UC-001 Standard: Process user corrections for ML improvement."""
        pass

    async def update_dossier(
        self,
        person_id: str,
        analysis_data: dict
    ) -> DossierUpdateResult:
        """UC-001 Standard: Update person dossier with new analysis."""
        pass
```

### **UC-001 Container-Standards:**
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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/uc001"]
```

---

## 📊 **UC-001 QUALITY GATES**

### **Evidence-Based Performance-Targets:**
- **Dossier-Update**: <Current_Baseline * 0.8 (20% improvement target)
- **Re-Identifikation**: >Current_Accuracy + 5% (gradual improvement)
- **Kleidungsklassifikation**: >85% bei 200+ Kategorien (benchmark-based)
- **Video-Analyse**: Hardware-relative Targets (Zeit pro MB, nicht absolut)
- **Parallel-Jobs**: >5 gleichzeitig ohne Degradation

### **UC-001 Specific Testing-Standards:**
```python
# PFLICHT für alle UC-001 Services:
class UC001TestSuite:
    """Extended tests for UC-001 features."""

    def test_person_dossier_creation(self):
        """Test: Person dossier is created correctly."""
        assert dossier.person_id is not None
        assert dossier.creation_timestamp is not None

    def test_re_identification_accuracy(self):
        """Test: Re-identification achieves >baseline+5% accuracy."""
        accuracy = self.measure_reidentification_accuracy()
        assert accuracy > (self.baseline_accuracy + 0.05)

    def test_user_correction_integration(self):
        """Test: User corrections improve accuracy over time."""
        initial_accuracy = self.measure_accuracy()
        self.apply_user_corrections(self.test_corrections)
        improved_accuracy = self.measure_accuracy()
        assert improved_accuracy > initial_accuracy

    def test_job_history_completeness(self):
        """Test: Job history contains all required fields."""
        history_entry = self.create_test_job_history()
        required_fields = ["person_id", "timestamp", "analysis_type", "results"]
        for field in required_fields:
            assert hasattr(history_entry, field)
```

---

## 🎨 **UC-001 CODE-STANDARDS**

### **Extended Docstring-Standards für UC-001:**
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
    UC-001: Analyze person in video for dossier system.

    This function performs comprehensive person analysis including
    face recognition, clothing classification, pose estimation,
    and behavioral pattern detection for the UC-001 Enhanced Manual
    Analysis system.

    Args:
        video_path: Absolute path to video file
        person_bbox: Bounding box coordinates for person detection
        analysis_config: UC-001 specific configuration parameters
        create_dossier: Whether to create new dossier if person not found
        update_existing: Whether to update existing dossier with new data

    Returns:
        UC001AnalysisResult containing:
            - person_id: Unique identifier for person
            - confidence_scores: Dictionary of confidence scores per analysis type
            - clothing_analysis: Detailed clothing categorization (200+ categories)
            - behavioral_patterns: Detected behavioral patterns over time
            - job_history_id: Reference to created job history entry

    Raises:
        FileNotFoundError: Video file not accessible
        UC001ValidationError: Invalid UC-001 configuration
        DossierCreationError: Failed to create or update dossier

    Example:
        >>> config = UC001Config(
        ...     enable_clothing_analysis=True,
        ...     clothing_categories=200,
        ...     enable_behavioral_tracking=True
        ... )
        >>> result = analyze_person_in_video(
        ...     "/path/to/video.mp4",
        ...     BoundingBox(x=100, y=50, w=200, h=400),
        ...     config
        ... )
        >>> print(f"Person ID: {result.person_id}")
        >>> print(f"Clothing: {result.clothing_analysis.primary_category}")
    """
    pass
```

---

## 🔧 **UC-001 DEVELOPMENT-WORKFLOW**

### **UC-001 Make-Targets:**
```bash
# UC-001 Development & Testing
make uc001-test              # UC-001 spezifische Tests
make uc001-validate          # Schema und Performance-Validierung
make uc001-demo              # Demo-Workflow ausführen

# UC-001 Deployment & Management
make uc001-deploy            # UC-001 Services deployen
make uc001-reset             # Services zurücksetzen
make dossier-check           # Dossier-System Health-Check

# UC-001 Monitoring & Logs
make uc001-status            # Status und Metriken anzeigen
make uc001-logs              # Service-Logs anzeigen
```

### **UC-001 Git-Workflow:**
```bash
# UC-001 Feature-Branch
git checkout -b feature/uc001-component-name
# UC-001 spezifische Entwicklung...
make uc001-test              # UC-001 Tests vor Commit
make uc001-validate          # Performance-Validierung
git commit -m "feat(uc001): component description"
```

---

## 📚 **UC-001 INTEGRATION-GUIDELINES**

### **Service-Integration-Reihenfolge:**
1. **person_dossier**: Core-Dossier-Management (Woche 1)
2. **video_context_analyzer**: LLM-basierte Video-Analyse (Woche 2)
3. **clothing_analyzer**: 200+ Kategorie-Klassifikation (Woche 3)
4. **job_manager**: UC-001 Job-Integration (Woche 4)
5. **ui_extensions**: Benutzer-Korrektur-Interface (Woche 5)

### **Inter-Service Communication:**
```python
# UC-001 Service-to-Service Communication Standard
class UC001MessageProtocol:
    """Standard protocol for UC-001 inter-service communication."""

    async def notify_dossier_update(
        self,
        person_id: str,
        update_type: str,
        data: dict
    ) -> None:
        """Notify other UC-001 services of dossier updates."""
        message = {
            "event": "dossier_updated",
            "person_id": person_id,
            "update_type": update_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        await self.publish_to_uc001_channel(message)
```

---

## 🎯 **UC-001 SUCCESS-CRITERIA**

### **Feature-Specific Goals:**
- ✅ **Dossier-System**: Vollständiges Personen-Management
- ✅ **Video-Kontext**: LLM-Integration für Szenen-Analyse
- ✅ **Kleidungs-Klassifikation**: 200+ Kategorien mit >85% Accuracy
- ✅ **Benutzer-Korrekturen**: ML-Verbesserung durch User-Feedback
- ✅ **Performance**: Evidence-based Targets erreicht

### **Integration Success:**
- ✅ **Service-Orchestration**: Alle UC-001 Services funktionieren zusammen
- ✅ **Data-Flow**: Nahtloser Datenfluss zwischen Services
- ✅ **User-Experience**: Intuitive Benutzer-Korrektur-Workflows
- ✅ **Monitoring**: Vollständige UC-001 Performance-Überwachung

---

**📝 Erstellt**: 02.01.2025
**🔗 Integration**: docs/UC-001-ENHANCED-MANUAL-ANALYSIS.md
**⚙️ Core-Rules**: .cursorrules (Feature-agnostic)
**🎯 Status**: BEREIT FÜR IMPLEMENTATION

🎮 POWER-USER KONTROLLE:
  Standard: CPU-First (kostenlos, privat, schnell)
  Enhanced: Cloud GPU (jederzeit aktivierbar, transparent, on-demand)
  Kontrolle: User entscheidet situativ was optimal ist

🔄 PRAKTISCHER WORKFLOW:
  1. System startet mit CPU-Verarbeitung (Option A)
  2. Cloud Enhancement wird IMMER als Option angezeigt
  3. User sieht: "☁️ Cloud Enhancement: +15% Genauigkeit, 4x schneller, $0.05"
  4. User klickt bei Bedarf auf Cloud Enhancement
  5. System nutzt beste verfügbare Cloud GPU Instanz

💡 BEST OF BOTH WORLDS:
  ✅ Alltägliche Tasks: Schnell, kostenlos, privat auf CPU
  ✅ Detaillierte Analysen: Ultra-Genauigkeit auf Cloud GPU
  ✅ Große Batches: 10x schnellere Verarbeitung in Cloud
  ✅ Experimental: Zugang zu GPT-4 Vision, Claude 3, etc.

# Use Case UC-001: Erweiterte Manuelle Medienanalyse mit Personen-Dossierung

**Use Case ID:** UC-001-ENHANCED-MANUAL-ANALYSIS
**Version:** 1.0
**Datum:** 06.02.2025
**Status:** Alpha 0.6.0 Implementierung
**Priorität:** Hoch

## 📋 Use Case Übersicht

### Ziel
**Als Benutzer möchte ich Videos und Bilder für eine manuelle Analyse hochladen können, um detaillierte Personen-Dossiers mit Fesselungs-, Kleidungs- und Verhaltensanalyse sowie Video-Kontext zu erstellen.**

### Akteure
- **Primärer Akteur:** Endbenutzer (Analyst/Forscher)
- **Sekundärer Akteur:** System (AI-Services, Job-Manager)

### Auslöser
Benutzer möchte Medien (Videos/Bilder) analysieren lassen

### Vorbedingungen
- System ist betriebsbereit
- Benutzer hat Zugang zur UI
- Job-Queue ist verfügbar

### Nachbedingungen (Erfolg)
- Medien sind analysiert
- Personen-Dossiers sind erstellt/aktualisiert
- Video-Kontext ist generiert
- Ergebnisse sind abrufbar

---

## 🔄 Hauptablauf (Success Scenario)

### Phase 1: Media Upload & Warteschlange
**1.1 Media-Upload**
```yaml
Akteur: Benutzer
Aktion: Lädt ein oder mehrere Videos/Bilder hoch
System-Reaktion:
  - Validiert Dateiformate (.mp4, .avi, .mov, .jpg, .png)
  - Speichert Medien in data/media/
  - Erstellt Job-Einträge in Redis-Queue
  - Generiert Job-ID für Tracking
```

**1.2 Vorschaubilder-Generierung**
```yaml
Trigger: Video-Upload erkannt
System-Aktion:
  - thumbnail_generator erstellt 4 Vorschaubilder (320x180px)
  - Speichert Thumbnails in data/frames/
  - Bei Bildserien: Erstellt Galerie-Übersicht
```

**1.3 Job-Bezeichnung & Kontext**
```yaml
Akteur: Benutzer
Aktion:
  - Ändert/erweitert Job-Bezeichnung
  - Fügt optional Kontext hinzu (Handlungen, Szenarien)
System-Reaktion:
  - Speichert Metadata in Job-Objekt
  - Markiert Job als "bereit für Analyse"
```

### Phase 2: Manuelle Analyse-Trigger
**2.1 Analyse-Start**
```yaml
Akteur: Benutzer
Aktion: Startet Analyse manuell (kein Real-Time)
System-Reaktion:
  - Überprüft Job-Queue Status
  - Startet AI-Processing-Pipeline
  - Setzt Job-Status auf "processing"
```

### Phase 3: AI-Service-Pipeline
**3.1 Basis-Analyse** (Parallel-Verarbeitung)
```yaml
Services:
  - face_reid: Gesichtserkennung und Embedding-Extraktion
  - restraint_detection: Fesselungs- und Material-Erkennung
  - clip_service: Erweiterte Kleidungsanalyse (Casual→Dessous)
  - pose_estimation: Körperhaltung und Bewegungsanalyse
  - whisper_transcriber: Audio-Transkription (bei Videos)
```

**3.2 Person-Dossier-Management**
```yaml
person_dossier Service:
  - Identifiziert Personen via Face-Embedding
  - Erstellt neue Dossiers oder aktualisiert bestehende
  - Generiert Porträtfotos (bestes Gesichtsfoto)
  - Extrahiert Körpermaße via Pose-Estimation
  - Klassifiziert Kleidung nach erweiterten Kategorien
```

**3.3 Video-Kontext-Analyse** (NEU)
```yaml
video_context_analyzer Service:
  - Analysiert Bewegungssequenzen über Zeit
  - Erkennt emotionale Ausdrücke und Verhaltensänderungen
  - Verarbeitet Audio-Aussagen und Reaktionen
  - Generiert LLM-basierten Kontext über Fesselungsgrund
  - Bewertet Verhalten der gefesselten Person
```

### Phase 4: Job-Historie & Dossier-Update
**4.1 Job-Historie-Eintrag**
```yaml
Für jede erkannte Person:
  - Erstellt JobHistoryEntry mit:
    - Handlungen und Bewegungen
    - Kleidung (detailliert: Casual→Dessous)
    - Emotionen und Ausdrücke
    - Audio-Aussagen und Reaktionen
    - Art der Fesselung mit Material-Benennung
    - Video-Kontext-Zusammenfassung
```

**4.2 Dossier-Aktualisierung**
```yaml
PersonDossier Update:
  - Hinzufügung neuer JobHistoryEntry
  - Update von Porträtfoto (wenn besseres gefunden)
  - Aktualisierung der Körpermaße
  - Erweiterung der Kleidungs-Statistiken
  - Hinzufügung neuer Fesselungs-Erfahrungen
```

### Phase 5: Benutzer-Intervention & Korrekturen
**5.1 Re-Identifikation-Korrektur**
```yaml
Akteur: Benutzer
UI-Funktionen:
  - Anzeige: "Person X als Person Y identifiziert?"
  - Korrektur-Optionen:
    - "Korrekt" → Bestätigung
    - "Falsch" → Zuordnung ändern
    - "Neue Person" → Separates Dossier erstellen
    - "Zusammenführen" → Zwei Dossiers vereinen
```

**5.2 Identifikations-Learning**
```yaml
System-Reaktion:
  - Speichert Benutzer-Korrekturen
  - Aktualisiert Face-Embeddings
  - Verbessert zukünftige Re-ID-Genauigkeit
  - Loggt Korrekturen für Audit-Trail
```

### Phase 6: Ergebnis-Abruf & Analyse
**6.1 Dossier-Anzeige**
```yaml
UI-Features:
  - Vollständige Personen-Galerie mit Porträts
  - Detaillierte Job-Historie pro Person
  - Körpermaße und physische Eigenschaften
  - Kleidungs-Analyse mit Kategorien
  - Fesselungs-Historie mit Materialien
  - Video-Kontext-Berichte
```

**6.2 Search & Filter**
```yaml
Such-Funktionen:
  - Nach Person (Gesicht, Name)
  - Nach Kleidungstyp ("Push-up BH", "Minirock")
  - Nach Fesselungs-Material ("Seil", "Handschellen")
  - Nach Zeitraum und Job-ID
  - Nach Video-Kontext-Inhalten
```

---

## 🆕 Erweiterte Features

### Detaillierte Kleidungsanalyse
```yaml
Kategorien-Spektrum:
  Casual: t-shirt, jeans, hoodie, sneakers
  Business: blazer, dress pants, business dress
  Formal: evening dress, suit, formal shoes
  Sportswear: gym clothes, athletic shorts, sports bra
  Intimate: bra, underwear, lingerie, stockings
  Fetish: latex, leather, vinyl, corset
  Materials: cotton, silk, leather, lace, satin
```

### Video-Kontext-Generierung
```yaml
Analyse-Dimensionen:
  Bewegungsanalyse:
    - Widerstandsbewegungen vs. Kooperation
    - Stress-Indikatoren (Zittern, Verkrampfung)
    - Bewegungseinschränkungen durch Fesselungen

  Emotionale-Analyse:
    - Gesichtsausdruck-Änderungen über Zeit
    - Audio-Emotionen (Freude, Angst, Schmerz)
    - Körpersprache-Interpretation

  Kontext-Generierung:
    - LLM-basierte Zusammenfassung der Situation
    - Grund der Fesselung (Training, Spiel, Bestrafung)
    - Bewertung des Verhaltens der gefesselten Person
```

### Erweiterte Personen-Dossiers
```yaml
JobHistoryEntry-Schema:
  job_id: string
  timestamp: datetime
  video_context_summary: string
  actions_detected: [
    {
      timestamp: "00:02:30",
      action: "resistance movement",
      intensity: "medium",
      description: "Person attempts to free hands from rope restraints"
    }
  ]
  clothing_analysis: {
    upper_body: "black lace bra (push-up style)",
    lower_body: "red mini skirt (above knee)",
    footwear: "black high heels (6 inch)",
    accessories: "silver collar, leather cuffs"
  }
  emotions_timeline: [
    {
      timestamp: "00:01:00",
      primary_emotion: "anxiety",
      confidence: 0.85,
      secondary_emotions: ["anticipation", "nervousness"]
    }
  ]
  restraints_detailed: {
    material: "rope (jute, 8mm)",
    technique: "shibari takate kote",
    body_parts: ["wrists", "upper arms", "torso"],
    restriction_level: "high",
    safety_assessment: "adequate circulation"
  }
  statements_audio: [
    {
      timestamp: "00:03:15",
      text: "Das ist zu eng",
      emotion: "discomfort",
      language: "german"
    }
  ]
```

---

## 🔧 Technische Implementation

### Service-Architektur
```yaml
Neue Services (Alpha 0.6.0):
  - video_context_analyzer: LLM-basierte Verhaltensanalyse
  - clothing_analyzer: Erweiterte CLIP-Kleidungserkennung
  - dossier_corrector: UI für Benutzer-Korrekturen

Erweiterte Services:
  - person_dossier: Job-Historie und erweiterte Schemas
  - clip_service: 200+ Kleidungskategorien
  - llm_service: Kontext-Generierung und Verhaltensanalyse
```

### API-Erweiterungen
```python
# Neue Endpoints
POST /dossiers/{id}/correct-identification
POST /dossiers/{id}/merge
GET /dossiers/search?clothing=miniskirt&material=leather
GET /jobs/{id}/video-context
POST /clothing/analyze-extended
```

### UI-Komponenten
```typescript
// Neue React-Komponenten
PersonDossierDetailView.tsx
JobHistoryTimeline.tsx
IdentificationCorrector.tsx
ClothingCategoryFilter.tsx
VideoContextViewer.tsx
```

---

## 📊 Erfolgsmetriken

### Funktionale Metriken
- ✅ Upload-to-Analysis-Pipeline: <2 Minuten
- ✅ Personen-Re-Identifikation: >90% Genauigkeit
- ✅ Kleidungs-Klassifikation: >85% Genauigkeit
- ✅ Video-Kontext-Qualität: Benutzer-Bewertung >4/5

### Performance-Metriken
- ✅ Job-Processing: 1080p Video in <5 Minuten
- ✅ Dossier-Update: <10 Sekunden
- ✅ UI-Response: <1 Sekunde für Dossier-Anzeige
- ✅ Parallel-Jobs: >5 gleichzeitig ohne Degradation

### Business-Metriken
- ✅ Benutzer-Adoption: >80% nutzen Korrekturfunktionen
- ✅ Dossier-Qualität: <5% falsche Re-Identifikationen
- ✅ Workflow-Effizienz: 60% Zeit-Ersparnis vs. manuell

---

## 🛠️ Implementation-Roadmap

### Alpha 0.6.0 (6-8 Wochen)
**Phase 1: Basis-Erweiterungen (Woche 1-2)**
- ✅ Erweiterte Kleidungskategorien
- ✅ Job-Historie-Schema
- ✅ UI-Basis-Erweiterungen

**Phase 2: Dossier-Features (Woche 3-4)**
- 🔄 Benutzer-Korrekturfunktionen
- 🔄 Porträtfoto-Integration
- 🔄 Körpermaße-Erfassung

**Phase 3: Video-Kontext (Woche 5-6)**
- 🆕 LLM-Kontext-Generierung
- 🆕 Verhaltensanalyse-Pipeline
- 🆕 Timeline-basierte Bewegungsanalyse

**Phase 4: Integration (Woche 7-8)**
- 🔧 End-to-End-Tests
- 🔧 Performance-Optimierung
- 🔧 UI-Polishing

---

## 🎯 Acceptance Criteria

### Definition of Done
- [ ] User kann Videos/Bilder hochladen und Job-Kontext hinzufügen
- [ ] System generiert automatisch Personen-Dossiers mit Porträts
- [ ] Kleidungsanalyse erkennt 200+ Kategorien (Casual→Dessous)
- [ ] Video-Kontext-Analyse generiert verständliche Berichte
- [ ] Benutzer kann Re-Identifikationen korrigieren
- [ ] Job-Historie zeigt detaillierte Analyse-Ergebnisse
- [ ] Such-/Filterfunktionen funktionieren nach allen Kriterien
- [ ] Performance-Ziele werden erreicht
- [ ] UI ist intuitiv und responsive

### Test-Szenarien
1. **Happy Path:** Upload → Analyse → Dossier → Korrektur → Suche
2. **Error Handling:** Falsche Re-ID → Korrektur → Dossier-Merge
3. **Performance:** 5 parallele Video-Analysen
4. **Edge Cases:** Identische Personen in verschiedenen Outfits
5. **Integration:** End-to-End mit Cloud AI-Services

---

**Geschätzter Aufwand:** 6-8 Wochen
**Risiko:** Niedrig (90% vorhandene Services)
**Dependencies:** Alpha 0.5.0 VPS-Production-Readiness

# AI Media Analysis System - Iterative Entwicklungs-Regelwerk
# Version: 1.0.0
# Status: Aktiv (Projektregel seit Alpha 0.5.0)

## Grundprinzip der iterativen Entwicklung

### Kernregel
**ALLE größeren Features und Service-Integrationen folgen dem 4-Iterations-Modell**

### Anwendungsbereiche
- Service-Integration (Alpha 0.5.0)
- Feature-Entwicklung (Alpha 0.6.0+)
- Performance-Optimierung
- Enterprise-Features
- VPS-Deployment-Prozesse

## 4-Iterations-Modell (Standard)

### Iteration 1: Core/Foundation
- **Zeitrahmen**: 1 Woche
- **Fokus**: Grundlegende Infrastruktur und Core-Services
- **Erfolgskriterium**: Basis-Funktionalität läuft stabil
- **Testing**: `make iteration-test ITERATION=1`

### Iteration 2: Processing/Logic
- **Zeitrahmen**: 1 Woche
- **Fokus**: Hauptverarbeitungslogik und AI-Pipeline
- **Erfolgskriterium**: End-to-End-Processing funktioniert
- **Testing**: `make iteration-test ITERATION=2`

### Iteration 3: Specialized/Advanced
- **Zeitrahmen**: 1 Woche
- **Fokus**: Spezialisierte Features und erweiterte Funktionen
- **Erfolgskriterium**: Alle geplanten Features implementiert
- **Testing**: `make iteration-test ITERATION=3`

### Iteration 4: UI/Integration
- **Zeitrahmen**: 1 Woche
- **Fokus**: User Interface und finale Integration
- **Erfolgskriterium**: Production-ready System
- **Testing**: `make iteration-test ITERATION=4`

## Makefile-Integration (Pflicht)

### Iteration-Commands (Standard)
```makefile
iteration-1: ## Iteration 1 ausführen
iteration-2: ## Iteration 2 ausführen
iteration-3: ## Iteration 3 ausführen
iteration-4: ## Iteration 4 ausführen
iteration-status: ## Status aller Iterationen anzeigen
iteration-test: ## Test für aktuelle Iteration (ITERATION=1-4)
integration-all: ## Alle 4 Iterationen sequenziell
```

### Service-Management (für Service-Integration)
```makefile
service-add: ## Service hinzufügen (SERVICE=name)
service-test: ## Service testen (SERVICE=name)
service-dockerfile-cpu: ## CPU-Dockerfile erstellen
```

## VPS-Constraint-Validation

### Memory-Limits pro Iteration
- **Iteration 1**: ≤12GB RAM (Management-Services)
- **Iteration 2**: ≤16GB RAM (+AI-Processing)
- **Iteration 3**: ≤20GB RAM (+Specialized-Services)
- **Iteration 4**: ≤24GB RAM (Full-Stack)

### Automatische Validierung
```bash
# Nach jeder Iteration
make vps-test
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"
```

## Rollback-Strategie (Pflicht)

### Automatische Backups
```bash
# Vor jeder Iteration
cp docker-compose.yml docker-compose.yml.backup.iteration-N
```

### Rollback-Commands
```makefile
rollback-iteration: ## Rollback zur vorherigen Iteration
	cp docker-compose.yml.backup.iteration-$(PREV) docker-compose.yml
	docker-compose down
	docker-compose up -d
```

## Testing-Standards pro Iteration

### Iteration-Gates (Pflicht)
Jede Iteration muss bestehen:

1. **Health-Checks**: Alle Services "healthy"
2. **Memory-Limits**: VPS-Constraints eingehalten
3. **Integration-Tests**: Inter-Service-Communication
4. **Performance-Tests**: Response-Time-Targets

### Test-Commands
```bash
# Standard-Tests pro Iteration
make iteration-test ITERATION=X
make health-check
make vps-test
make test-integration
```

## Git-Workflow pro Iteration

### Branch-Strategie
```bash
# Neue Iteration
git checkout -b feature/iteration-X-description
git commit -m "🔄 Iteration X: [Component] - [Achievement]"

# Nach erfolgreichem Test
git checkout main
git merge feature/iteration-X-description
git tag "alpha-0.X.0-iteration-X"
```

### Commit-Nachrichten
```bash
# Standard-Format
🔄 Iteration 1: Management-Core - 4 Services integriert
🔄 Iteration 2: AI-Pipeline - End-to-End Processing aktiv
🔄 Iteration 3: Specialized-Detection - UC-001 Features
🔄 Iteration 4: Production-UI - Content-Moderation vollständig
```

## Dokumentations-Updates (Pflicht)

### Nach jeder Iteration aktualisieren:
- `PROJECT_STATE.md`: Service-Status
- `ROADMAP.md`: Fortschritt markieren
- `CHANGELOG.md`: Iteration-Achievements

### Template für PROJECT_STATE.md
```markdown
## Alpha 0.X.0 - Iteration X Status ✅

### Erreichte Services (X/24)
- **Infrastructure**: [Liste]
- **AI Processing**: [Liste]
- **Management**: [Liste]
- **UI**: [Liste]

### Performance-Metrics
- **Memory-Verbrauch**: XGB/24GB
- **Service-Health**: X/X healthy
- **Response-Times**: <Xs average
```

## Iteration-Planning-Template

### Vor jeder Iteration definieren:

```markdown
## Iteration X: [Name] (Woche X)

### 🎯 Hauptziel
[Klares, messbares Ziel]

### 📋 Services/Features (X Services)
- [ ] **Service 1**: [Beschreibung] - Priority ⚡
- [ ] **Service 2**: [Beschreibung] - Priority ⚡
- [ ] **Service 3**: [Beschreibung] - Priority ⚡

### 📊 Erfolgskriterien
- [ ] Alle X Services laufen stabil
- [ ] Memory-Verbrauch <XGB
- [ ] Integration-Tests grün
- [ ] [Spezifische Funktionalität] demonstrierbar

### 🛠️ Technische Deliverables
- docker-compose.yml mit X Services
- Dockerfile.cpu für neue Services
- Health-Checks implementiert
- Makefile-Commands funktionsfähig
```

## Performance-Monitoring (Kontinuierlich)

### Metrics pro Iteration
```bash
# Automatisches Monitoring
make monitor

# Iteration-Vergleich
echo "Iteration X Metrics:" > metrics/iteration-X.log
docker stats --no-stream >> metrics/iteration-X.log
```

### Performance-Thresholds
- **Memory**: Max 6GB pro neue Service-Gruppe
- **CPU**: Max 2 Cores pro Service
- **Response-Time**: <5s für AI-Processing
- **Health-Check**: <30s für Service-Start

## Fehlerbehandlung und Lessons Learned

### Iteration-Retrospektive (nach jeder Iteration)
```markdown
## Iteration X Retrospektive

### ✅ Was lief gut
- [Erfolgreiche Aspekte]

### ❌ Probleme
- [Aufgetretene Probleme]

### 🔄 Verbesserungen für nächste Iteration
- [Konkrete Anpassungen]

### 📊 Metrics
- Zeit: X Stunden/Tage
- Services: X erfolgreich integriert
- Tests: X/X bestanden
```

## Best Practices

### DO's ✅
- Immer vollständige Iteration abschließen vor nächster
- Automatische Tests nach jeder Iteration
- Memory-Limits kontinuierlich überwachen
- Dokumentation parallel zur Entwicklung aktualisieren
- Service-Dependencies explizit definieren

### DON'Ts ❌
- Keine partiellen Iterationen committen
- Keine Iteration ohne vollständige Tests
- Keine Memory-Limit-Überschreitungen ignorieren
- Keine Service-Integration ohne Health-Checks
- Keine Rollback-Strategie überspringen

## Tools und Automatisierung

### Erforderliche Scripts
- `scripts/generate_service_config.py`: Service-Konfiguration
- `scripts/iteration-status.sh`: Status-Monitoring
- `scripts/health-check-all.sh`: Comprehensive Health-Checks

### CI/CD-Integration
```yaml
# .github/workflows/iteration-test.yml
name: Iteration Test
on:
  push:
    branches: [ "feature/iteration-*" ]
jobs:
  iteration-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Iteration Tests
        run: make iteration-test ITERATION=${{ github.ref_name | sed 's/.*iteration-\([0-9]\).*/\1/' }}
```

## Skalierung für größere Features

### Für komplexere Features (>4 Wochen)
- **Sub-Iterationen**: 2-Wochen-Zyklen mit Mini-Iterationen
- **Feature-Flags**: Schrittweise Aktivierung
- **A/B-Testing**: Parallele Implementierungen testen

### Multi-Team-Koordination
- **Iteration-Sync**: Wöchentliche Iteration-Reviews
- **Dependency-Management**: Service-Dependencies explizit koordinieren
- **Resource-Sharing**: VPS-Memory fair aufteilen

---

**Diese iterative Entwicklungsregel ist bindend für alle Entwicklungsaktivitäten im AI Media Analysis-Projekt ab Alpha 0.5.0**

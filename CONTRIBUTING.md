# Beitragsrichtlinien

## Übersicht

Wir freuen uns über Ihre Beiträge zu diesem Projekt. Diese Richtlinien sollen Ihnen helfen, effektiv mitzuarbeiten.

## Entwicklungsprozess

### Branch-Strategie

- `main`: Produktionscode
- `develop`: Entwicklungszweig
- `feature/*`: Neue Features
- `bugfix/*`: Fehlerbehebungen
- `hotfix/*`: Dringende Produktionsfixes

### Workflow

1. Fork des Repositories
2. Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'feat: add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request erstellen

## Code-Standards

### Python

- PEP 8 Konventionen
- Typisierung mit Python Type Hints
- Docstrings für alle Funktionen und Klassen
- Unit Tests für neue Features

```python
def process_frame(frame: np.ndarray, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verarbeitet einen einzelnen Frame.

    Args:
        frame: NumPy Array mit Bilddaten
        config: Konfigurationsdictionary

    Returns:
        Dictionary mit Analyseergebnissen
    """
    pass
```

### JavaScript/TypeScript

- ESLint Konfiguration
- TypeScript für Typ-Sicherheit
- JSDoc für Dokumentation
- Jest für Tests

```typescript
/**
 * Verarbeitet einen Frame
 * @param frame - Bilddaten als Array
 * @param config - Konfigurationsobjekt
 * @returns Analyseergebnisse
 */
async function processFrame(
    frame: number[],
    config: Config
): Promise<AnalysisResult> {
    // Implementation
}
```

## Commit-Nachrichten

Format: `type(scope): description`

Typen:
- `feat`: Neue Feature
- `fix`: Fehlerbehebung
- `docs`: Dokumentation
- `style`: Formatierung
- `refactor`: Code-Umstrukturierung
- `test`: Tests
- `chore`: Wartung

Beispiele:
```
feat(api): add new endpoint for batch processing
fix(detector): correct memory leak in frame analysis
docs(readme): update installation instructions
```

## Pull Requests

1. Beschreibung des Problems/Features
2. Änderungen im Detail
3. Tests und Dokumentation
4. Screenshots (falls relevant)
5. Checkliste:
   - [ ] Tests hinzugefügt
   - [ ] Dokumentation aktualisiert
   - [ ] Code-Review durchgeführt
   - [ ] CI-Tests bestanden

## Entwicklungsumgebung

### Voraussetzungen

- Python 3.8+
- Node.js 16+
- Docker
- CUDA-kompatible GPU

### Setup

1. Repository klonen
```bash
git clone https://github.com/username/ai_media_analysis.git
cd ai_media_analysis
```

2. Virtuelle Umgebung erstellen
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Entwicklungsserver starten
```bash
python -m uvicorn main:app --reload
```

## Tests

### Python Tests

```bash
pytest tests/
pytest tests/ --cov=services
```

### JavaScript Tests

```bash
npm test
npm run test:coverage
```

## Dokumentation

- Code-Dokumentation mit Docstrings
- API-Dokumentation in `API.md`
- README.md für Projektübersicht
- CHANGELOG.md für Änderungshistorie

## Code-Review

1. Funktionalität
2. Code-Qualität
3. Performance
4. Sicherheit
5. Wartbarkeit

## Lizenz

Mit der Einreichung eines Pull Requests stimmen Sie zu, dass Ihre Änderungen unter der MIT-Lizenz veröffentlicht werden. 
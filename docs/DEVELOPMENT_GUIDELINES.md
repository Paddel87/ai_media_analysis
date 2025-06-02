# AI Media Analysis - Entwicklungsrichtlinien

## 🎯 Übersicht

Diese Richtlinien stellen sicher, dass der Code des AI Media Analysis Systems konsistent, wartbar und qualitativ hochwertig bleibt.

## 🎨 Code-Formatierung

### Automatische Tools

Das Projekt verwendet folgende automatische Formatierungs-Tools:

- **Black**: Code-Formatierung (Zeilenlänge: 88 Zeichen)
- **isort**: Import-Sortierung (Profil: black-kompatibel)
- **flake8**: Linting und Stil-Checks
- **mypy**: Type-Checking (optional, aber empfohlen)

### Konfiguration

Alle Tools sind in `pyproject.toml` konfiguriert. Die Einstellungen sind projektspezifisch optimiert.

## 🛠️ Verwendung der Formatierungs-Tools

### Lokale Entwicklung

```bash
# Automatische Formatierung (empfohlen vor Commits)
make format

# Formatierung prüfen ohne Änderungen
make check-format

# Vollständiges Linting
make lint

# Alles in einem (Formatierung + Linting)
make fix-all
```

### Scripts verwenden

```bash
# Bash (Linux/macOS)
./scripts/format-check.sh --fix

# PowerShell (Windows)
.\scripts\format-check.ps1 -Fix
```

### Pre-Commit-Hooks

```bash
# Pre-Commit-Hooks installieren (einmalig)
make pre-commit-install

# Pre-Commit-Hooks manuell ausführen
make pre-commit-run
```

## 📋 Code-Stil-Richtlinien

### Python-Code

1. **Zeilenlänge**: Maximal 88 Zeichen (Black-Standard)
2. **Import-Sortierung**: Nach isort-Konfiguration
3. **Docstrings**: Google-Stil bevorzugt
4. **Type-Hints**: Verwende wo möglich
5. **Trailing Whitespace**: Nicht erlaubt
6. **End-of-File**: Muss mit Newline enden

### Datei-Struktur

```python
# AI Media Analysis - Service Name
# Beschreibung des Services

import standard_library
import third_party_libraries
import local_imports

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konstanten
KONSTANTE = "wert"

# Klassen und Funktionen
```

### Import-Reihenfolge (isort)

1. Standard-Library-Imports
2. Third-Party-Imports  
3. Local-Imports (services, common)

Beispiel:
```python
import json
import logging
import os

import torch
import fastapi
import redis

from common.logging_config import ServiceLogger
from services.base import BaseService
```

### Kommentare und Docstrings

```python
def process_data(data: List[Dict], config: Dict) -> Dict:
    """
    Verarbeitet eingehende Daten basierend auf Konfiguration.
    
    Args:
        data: Liste von Datenelementen
        config: Konfigurationsparameter
        
    Returns:
        Verarbeitungsergebnis
        
    Raises:
        ValueError: Bei ungültigen Eingabedaten
    """
    # Implementierung hier
    pass
```

## 🔧 Entwicklungs-Workflow

### Vor jedem Commit

1. **Automatische Formatierung ausführen**:
   ```bash
   make format
   ```

2. **Code-Qualität prüfen**:
   ```bash
   make lint
   ```

3. **Tests ausführen**:
   ```bash
   make test-unit
   ```

### CI/CD-Integration

Die GitHub Actions Pipeline prüft automatisch:
- Black-Formatierung
- isort-Import-Sortierung  
- flake8-Linting
- mypy Type-Checking
- Test-Coverage

## 🚫 Häufige Fehler vermeiden

### isort-Probleme

```python
# ❌ Falsch - Leerzeile zwischen third-party und local imports
import torch
import whisper

from common.base import BaseService

# ✅ Richtig - Korrekte Gruppierung
import torch
import whisper
from common.base import BaseService
```

### Black-Probleme

```python
# ❌ Falsch - Trailing Whitespace
def function():  
    pass

# ✅ Richtig - Kein Trailing Whitespace
def function():
    pass
```

### flake8-Probleme

```python
# ❌ Falsch - Zu lange Zeile
very_long_variable_name = some_very_long_function_call_with_many_parameters(param1, param2, param3, param4)

# ✅ Richtig - Umbruch
very_long_variable_name = some_very_long_function_call_with_many_parameters(
    param1, param2, param3, param4
)
```

## 🔍 IDE-Konfiguration

### VS Code (.vscode/settings.json)

```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile=black"],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--max-line-length=88", "--extend-ignore=E203,W503"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. **Black-Integration**: External Tools konfigurieren
2. **isort-Integration**: External Tools konfigurieren  
3. **Auto-Format on Save**: aktivieren
4. **flake8**: als Code-Inspector konfigurieren

## 🎯 Automatisierung

### Pre-Commit-Hooks

Nach der Installation mit `make pre-commit-install` werden automatisch bei jedem Commit folgende Checks ausgeführt:

- Trailing Whitespace entfernen
- End-of-File-Fixer
- YAML-Syntax prüfen
- Black-Formatierung
- isort-Import-Sortierung
- flake8-Linting

### Makefile-Targets

| Target | Beschreibung |
|--------|-------------|
| `make format` | Automatische Code-Formatierung |
| `make check-format` | Formatierung prüfen ohne Änderungen |
| `make lint` | Vollständiges Linting |
| `make fix-all` | Formatierung + Linting |
| `make pre-commit-install` | Pre-Commit-Hooks installieren |
| `make pre-commit-run` | Pre-Commit-Hooks manuell ausführen |

## 📊 Qualitätskontrolle

### Code-Coverage

- **Minimum**: 70% Test-Coverage
- **Ziel**: 80%+ Test-Coverage  
- **Reports**: HTML-Reports in `htmlcov/`

### Performance-Guidelines

- **Batch-Size**: Dynamisch an GPU-Speicher anpassen
- **Memory-Management**: GPU-Speicher nach Verarbeitung bereinigen
- **Caching**: Redis für häufig verwendete Daten
- **Logging**: Strukturierte Logs mit Kontext

## 🚀 Continuous Integration

### GitHub Actions

Die CI-Pipeline führt automatisch aus:

1. **Formatierungs-Checks**: Black, isort
2. **Code-Qualität**: flake8, mypy  
3. **Tests**: Unit-Tests, Integration-Tests
4. **Security**: Bandit Security-Scan
5. **Dependencies**: Safety Vulnerability-Check

### Lokale CI-Simulation

```bash
# Simuliere GitHub Actions lokal
make ci-local
```

## 📝 Dokumentation

### Code-Dokumentation

- **Docstrings**: Für alle öffentlichen Funktionen/Klassen
- **Type-Hints**: Für Parameter und Rückgabewerte
- **Inline-Kommentare**: Für komplexe Logik

### Projekt-Dokumentation

- **README.md**: Projekt-Übersicht und Setup
- **CHANGELOG.md**: Versionshistorie  
- **API-Docs**: Automatisch generiert via FastAPI
- **Architecture-Docs**: In `docs/` Verzeichnis

## 🎯 Fazit

Diese Richtlinien gewährleisten:
- **Konsistente Code-Qualität**
- **Automatisierte Formatierung**  
- **Vorbeugende Fehlererkennung**
- **Reibungslose CI/CD-Pipeline**
- **Professionelle Entwicklungsstandards**

Bei Fragen oder Problemen: Verwende die bereitgestellten Scripts und Makefile-Targets für automatische Korrektur. 
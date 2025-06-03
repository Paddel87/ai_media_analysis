# AI Media Analysis System - Black Code Standard Regel
# Version: 1.0.0
# Status: Aktiv - OBLIGATORISCH für alle Python-Dateien

## Black-Standard-Philosophie
- **Einheitlichkeit über Persönlichkeit**: Konsistente Formatierung im gesamten Codebase
- **Zero-Configuration**: Black-Standardeinstellungen ohne Anpassungen
- **Automatisierung**: Formatierung erfolgt automatisch vor jedem Commit
- **Strict Compliance**: Keine Abweichungen vom Black-Standard erlaubt
- **Developer Experience**: Weniger Zeit für Formatierung, mehr für Features

## Obligatorische Black-Standard-Anforderungen

### 1. Black-Konfiguration (PFLICHT)
- **Line Length**: Maximum 88 Zeichen (Black-Standard)
- **Target Version**: Python 3.11+
- **String Normalization**: Doppelte Anführungszeichen bevorzugt
- **No Custom Options**: Standard Black-Konfiguration ohne Modifikationen

```toml
# pyproject.toml - Black Konfiguration
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Verzeichnisse die ausgeschlossen werden
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.pytest_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
  # Spezifische Dateien
  | migrations/
)/
'''
```

### 2. Import-Sortierung mit isort (PFLICHT)
- **Black-Kompatibilität**: isort mit Black-Profil
- **Multi-Line-Output**: Mode 3 (Vertical Hanging Indent)
- **Line Length**: 88 Zeichen (matching Black)
- **Force Grid Wrap**: False für bessere Lesbarkeit

```toml
# pyproject.toml - isort Konfiguration
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### 3. Code-Beispiele

#### ✅ Korrekt - Black-konform
```python
"""Modul-Docstring mit doppelten Anführungszeichen."""

import os
import sys
from typing import Dict, List, Optional

import redis
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class ServiceConfig(BaseModel):
    """Service-Konfiguration mit klarer Typisierung."""

    name: str
    port: int = 8000
    debug: bool = False
    features: List[str] = []


def process_video(
    video_path: str,
    output_dir: str,
    config: Optional[ServiceConfig] = None,
    *,
    batch_size: int = 1,
) -> Dict[str, any]:
    """
    Verarbeitet Video mit konfigurierbaren Parametern.

    Args:
        video_path: Pfad zur Videodatei
        output_dir: Ausgabeverzeichnis
        config: Optionale Service-Konfiguration
        batch_size: Batch-Größe für Verarbeitung

    Returns:
        Verarbeitungsresultat als Dictionary
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video nicht gefunden: {video_path}")

    result = {
        "status": "success",
        "processed_frames": 0,
        "output_path": output_dir,
        "metadata": {"batch_size": batch_size},
    }

    # Komplexe Liste wird automatisch formatiert
    processing_steps = [
        "frame_extraction",
        "object_detection",
        "face_recognition",
        "nsfw_detection",
        "result_aggregation",
    ]

    for step in processing_steps:
        # Black formatiert automatisch
        if step == "frame_extraction" and config and config.debug:
            print(f"Debug: Ausführung von {step}")

    return result
```

#### ❌ Inkorrekt - Nicht Black-konform
```python
# Single quotes, inconsistent spacing
import os,sys
from typing import Dict,List,Optional
import redis,uvicorn
from fastapi import FastAPI,HTTPException

class ServiceConfig( BaseModel ):
    name:str
    port:int=8000
    debug:bool=False

def process_video(video_path:str,output_dir:str,config:Optional[ServiceConfig]=None,*,batch_size:int=1)->Dict[str,any]:
    if not os.path.exists( video_path ):
        raise FileNotFoundError( f'Video nicht gefunden: {video_path}' )

    result={'status':'success','processed_frames':0,'output_path':output_dir,'metadata':{'batch_size':batch_size}}

    processing_steps=['frame_extraction','object_detection','face_recognition','nsfw_detection','result_aggregation']

    for step in processing_steps:
        if step=='frame_extraction' and config and config.debug:print(f'Debug: Ausführung von {step}')

    return result
```

## Automatisierung und Enforcement

### Pre-commit Hooks (OBLIGATORISCH)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--target-version=py311]

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

### Makefile-Targets
```makefile
# Automatische Formatierung
format: ## Formatiert Code mit Black und isort
	@echo "🎨 Formatiere Python-Code mit Black..."
	python -m black services/ tests/ scripts/
	@echo "🔧 Sortiere Imports mit isort..."
	python -m isort services/ tests/ scripts/ --profile black
	@echo "✅ Code-Formatierung abgeschlossen"

check-format: ## Prüft Code-Formatierung ohne Änderungen
	@echo "🔍 Prüfe Black-Formatierung..."
	python -m black --check --diff services/ tests/ scripts/
	@echo "🔍 Prüfe isort-Formatierung..."
	python -m isort --check-only --diff services/ tests/ scripts/
	@echo "✅ Formatierungs-Check abgeschlossen"

format-check-strict: ## Strenger Formatierungs-Check für CI/CD
	@echo "🚨 Strenger Black-Standard-Check..."
	python -m black --check services/ tests/ scripts/ || (echo "❌ Black-Formatierung fehlgeschlagen" && exit 1)
	python -m isort --check-only services/ tests/ scripts/ || (echo "❌ Import-Sortierung fehlgeschlagen" && exit 1)
	@echo "✅ Strenger Formatierungs-Check erfolgreich"
```

### GitHub Actions Integration
```yaml
# .github/workflows/black-standard.yml
name: Black Code Standard Check
on: [push, pull_request]

jobs:
  black-standard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install formatting tools
        run: |
          pip install black isort

      - name: Check Black formatting
        run: |
          black --check --diff services/ tests/ scripts/

      - name: Check import sorting
        run: |
          isort --check-only --diff services/ tests/ scripts/

      - name: Fail if formatting issues found
        run: |
          echo "❌ Code-Formatierung entspricht nicht dem Black-Standard!"
          echo "🔧 Führe 'make format' aus, um Probleme zu beheben"
          exit 1
        if: failure()
```

## Entwickler-Workflow

### 1. Initiales Setup
```bash
# Black-Standard-Umgebung einrichten
make install-dev
pre-commit install

# Bestehenden Code formatieren
make format
```

### 2. Täglicher Workflow
```bash
# Vor dem Commit automatisch formatieren
git add .
# Pre-commit Hook formatiert automatisch
git commit -m "Feature implemented"

# Oder manuell formatieren
make format
git add .
git commit -m "Feature implemented"
```

### 3. CI/CD Integration
- **Pull Request**: Automatischer Black-Check
- **Merge**: Nur bei erfolgreicher Formatierung
- **Deploy**: Black-Standard ist Voraussetzung

## IDE Integration

### VS Code Settings
```json
// .vscode/settings.json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--target-version", "py311"],
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": ["--max-line-length=88", "--ignore=E203,W503"]
}
```

### PyCharm Settings
- **File → Settings → Tools → External Tools**
- **Black**: Add external tool with `black $FilePath$`
- **isort**: Add external tool with `isort $FilePath$ --profile black`

## Enforcement-Mechanismen

### 1. Pre-commit Prevention
```bash
# Commit wird blockiert bei Formatierungsfehlern
$ git commit -m "New feature"
black................................................................Failed
- hook id: black
- files were modified by this hook

isort................................................................Failed
- hook id: isort
- files were modified by this hook

# Automatic fix and retry
Files reformatted. Please add and commit again.
```

### 2. CI/CD Pipeline Failure
```yaml
❌ Build failed - Black standard violated
- services/new_service/main.py: Line too long (92 > 88 characters)
- tests/test_feature.py: Import sorting incorrect
```

### 3. Code Review Requirements
- **Automated Check**: GitHub Status Check muss erfolgreich sein
- **Review Blocker**: PR kann nicht gemerged werden bei Formatierungsfehlern
- **Bot Comments**: Automatische Kommentare bei Formatierungsproblemen

## Ausnahmen und Edge Cases

### Temporäre Deaktivierung (NUR in Ausnahmefällen)
```python
# fmt: off
manually_formatted_matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
# fmt: on

# Für spezielle Formatierung die lesbarere ist
```

### Legacy Code Migration
```python
# Legacy-Code schrittweise migrieren
# 1. Datei-weise Black-Formatierung
# 2. Kommit pro formatierte Datei
# 3. Keine funktionalen Änderungen mit Formatierung mischen
```

## Monitoring und Metriken

### Code-Qualitäts-Dashboard
- **Formatierungs-Compliance**: 100% für neue Dateien
- **Pre-commit-Erfolgsrate**: > 95%
- **CI/CD-Failure-Rate**: < 5% durch Formatierung
- **Developer-Productivity**: Weniger Zeit für Code-Review-Formatierungs-Diskussionen

### Automatisierte Reports
```bash
# Weekly formatting compliance report
make format-report

# Black-Standard Violations Report
make black-violations-report
```

## Integration mit anderen Regeln

### Verbindung zu Feature Testing
- **Test-Code**: Unterliegt denselben Black-Standards
- **Test-Fixtures**: Müssen Black-konform sein
- **Mock-Daten**: Automatische Formatierung

### Verbindung zu Dokumentation
- **Code-Beispiele**: Müssen Black-formatiert sein
- **README-Code-Blöcke**: Black-Standard in Dokumentation
- **API-Dokumentation**: Konsistente Code-Beispiele

### Verbindung zu Iterative Development
- **Iteration Commits**: Formatierung vor jedem Iterations-Commit
- **Service Integration**: Neuer Service-Code muss Black-konform sein
- **Legacy Refactoring**: Schrittweise Formatierung bei Code-Updates

## Schulung und Adoption

### Developer Onboarding
1. **Black-Standard-Workshop**: Einführung in Philosophie und Tools
2. **IDE-Setup-Session**: Konfiguration der Entwicklungsumgebung
3. **Hands-on-Training**: Praktische Übungen mit Black-Formatierung
4. **Code-Review-Training**: Black-Standard in Reviews berücksichtigen

### Best Practices Guide
- **Commit-Hygiene**: Formatierungs-Commits vs. Feature-Commits trennen
- **Branch-Management**: Feature-Branches vor Merge formatieren
- **Code-Review**: Fokus auf Logic, nicht auf Formatierung
- **Legacy-Migration**: Strategien für bestehenden Code

## Troubleshooting

### Häufige Probleme

#### "Line too long" Fehler
```python
# ❌ Problem
very_long_function_call(parameter1, parameter2, parameter3, parameter4, parameter5, parameter6)

# ✅ Lösung - Black formatiert automatisch
very_long_function_call(
    parameter1,
    parameter2,
    parameter3,
    parameter4,
    parameter5,
    parameter6
)
```

#### Import-Konflikte zwischen Black und isort
```bash
# Lösung: isort mit Black-Profil verwenden
isort --profile black file.py
```

#### Pre-commit Hook schlägt fehl
```bash
# Diagnose
pre-commit run --all-files

# Fix
make format
git add .
git commit --no-verify  # NUR in Notfällen
```

## Version und Updates

### Black-Version-Management
- **Locked Version**: Spezifische Black-Version in requirements.txt
- **Update-Strategie**: Koordinierte Updates über alle Entwickler
- **Regression-Testing**: Tests nach Black-Updates

### Konfiguration-Evolution
- **Backwards Compatibility**: Vorsichtige Konfigurationsänderungen
- **Team Communication**: Änderungen werden kommuniziert
- **Migration Guide**: Schritt-für-Schritt Updates

---

## 🎯 Status: AKTIV - Obligatorisch für alle Python-Dateien

Diese Regel ist **sofort wirksam** und gilt für:
- ✅ Alle neuen Python-Dateien
- ✅ Alle geänderten Python-Dateien
- ✅ Alle Commits und Pull Requests
- ✅ CI/CD Pipeline-Validierung
- ✅ Code Review Requirements

**Kein Python-Code ohne Black-Standard-Compliance!** 🎨✨

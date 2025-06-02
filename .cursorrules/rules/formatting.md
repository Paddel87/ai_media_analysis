# AI Media Analysis System - Formatierungs-Regelwerk
# Version: 1.0.0
# Status: Aktiv

## Black Formatierung (Strikt!)

### Grundregeln
- **Line Length**: 88 Zeichen (Black Standard)
- **Target Version**: Python 3.11+
- **String Quotes**: Doppelte Anführungszeichen für Strings
- **Trailing Commas**: Immer in mehrzeiligen Strukturen
- **Empty Lines**: Zwei Leerzeilen vor Top-Level-Klassen/Funktionen

### Automatisierung
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--line-length=88, --target-version=py311]
```

## Import-Sortierung (isort)

### Grundregeln
- **Profile**: Black-kompatibel
- **Sections**:
  1. Standard Library
  2. Third Party
  3. Local Application
- **Line Length**: 88 Zeichen
- **Multi-Line**: 3+ Imports

### Automatisierung
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black", "--line-length", "88"]
```

## Typ-Annotationen

### Grundregeln
- **Strict Mode**: Aktiviert
- **Check Untyped Defs**: Aktiviert
- **Disallow Untyped Defs**: Aktiviert
- **Disallow Incomplete Defs**: Aktiviert

### Automatisierung
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict, --ignore-missing-imports]
```

## Code-Style-Checks (flake8)

### Grundregeln
- **Max Line Length**: 88 Zeichen
- **Ignore Rules**:
  - E203 (Black-kompatibel)
  - W503 (Black-kompatibel)
- **Complexity**:
  - Max Complexity: 10
  - Max Arguments: 5
  - Max Local Variables: 15

### Automatisierung
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --ignore=E203,W503]
```

## VSCode Integration

### settings.json
```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "editor.formatOnSave": true,
    "editor.rulers": [88],
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true
}
```

## CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/format-check.yml
name: Format Check
on: [push, pull_request]
jobs:
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: |
          python -m pip install --upgrade pip
          pip install black isort flake8 mypy
      - run: |
          black --check --diff .
          isort --check-only --profile black .
          flake8 .
          mypy .
```

## Entwicklungsworkflow

### Pre-Commit Hooks
1. **Black**: Automatische Formatierung
2. **isort**: Import-Sortierung
3. **flake8**: Style-Checks
4. **mypy**: Typ-Checks

### Manuelle Überprüfung
```bash
# Formatierung prüfen
black --check --diff .

# Imports prüfen
isort --check-only --profile black .

# Style prüfen
flake8 .

# Typen prüfen
mypy .
```

## Best Practices

### Code-Formatierung
1. **Strings**:
   ```python
   # ✅ Korrekt
   message = "Hallo Welt"

   # ❌ Falsch
   message = 'Hallo Welt'
   ```

2. **Listen/Dictionaries**:
   ```python
   # ✅ Korrekt
   items = [
       "eins",
       "zwei",
       "drei",
   ]

   # ❌ Falsch
   items = ["eins", "zwei", "drei"]
   ```

3. **Funktionsdefinitionen**:
   ```python
   # ✅ Korrekt
   def process_data(
       data: List[str],
       options: Optional[Dict[str, Any]] = None,
   ) -> Dict[str, Any]:
       pass

   # ❌ Falsch
   def process_data(data:List[str],options:Optional[Dict[str,Any]]=None)->Dict[str,Any]:
       pass
   ```

### Import-Sortierung
```python
# ✅ Korrekt
import os
import sys
from typing import Dict, List, Optional

import numpy as np
import torch
from fastapi import FastAPI

from .config import get_settings
from .models import DataModel

# ❌ Falsch
from .models import DataModel
import torch
import os
from fastapi import FastAPI
import numpy as np
from .config import get_settings
import sys
from typing import Dict, List, Optional
```

## Fehlerbehandlung

### Formatierungsfehler
1. **Black-Fehler**:
   - Automatische Korrektur mit `black .`
   - Manuelle Überprüfung der Änderungen

2. **isort-Fehler**:
   - Automatische Korrektur mit `isort .`
   - Überprüfung der Import-Struktur

3. **flake8-Fehler**:
   - Manuelle Korrektur der Style-Probleme
   - Dokumentation der Ausnahmen

4. **mypy-Fehler**:
   - Korrektur der Typ-Annotationen
   - Dokumentation der `# type: ignore` Kommentare

## Dokumentation

### Formatierungsregeln
- In `CONTRIBUTING.md` dokumentieren
- In Team-Meetings besprechen
- Regelmäßige Reviews durchführen

### Ausnahmen
- Mit `# fmt: off/on` markieren
- In Code-Reviews dokumentieren
- In Team-Meetings besprechen

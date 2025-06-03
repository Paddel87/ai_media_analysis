# AI Media Analysis System - Black Code Standard Regel
# Version: 2.0.0 - Fokussiert auf Black-Details
# Status: Aktiv - OBLIGATORISCH für alle Python-Dateien
# Verweis: Master-Formatierungsregel siehe `.cursorrules.formatting`

## Black-Standard-Philosophie
- **Einheitlichkeit über Persönlichkeit**: Konsistente Formatierung im gesamten Codebase
- **Zero-Configuration**: Black-Standardeinstellungen ohne Anpassungen
- **Automatisierung**: Formatierung erfolgt automatisch vor jedem Commit
- **Strict Compliance**: Keine Abweichungen vom Black-Standard erlaubt

## Detaillierte Black-Konfiguration

### pyproject.toml - Black Setup
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # Verzeichnisse die ausgeschlossen werden
  \.eggs
  | \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.tox
  | \.venv
  | venv
  | migrations/
)/
'''
```

### isort - Black-Kompatible Konfiguration
```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

## Black-spezifische Code-Beispiele

### String-Formatierung
```python
# ✅ Black-Standard: Doppelte Anführungszeichen
message = "Hallo Welt"
f_string = f"Ergebnis: {result}"

# ❌ Nicht Black-konform
message = 'Hallo Welt'
old_format = "Ergebnis: %s" % result
```

### Komplexe Funktionsparameter
```python
# ✅ Black-konforme Formatierung
async def complex_video_processing(
    video_path: str,
    output_directory: str,
    analysis_config: Dict[str, Any],
    *,
    batch_size: int = 32,
    parallel_workers: int = 4,
    enable_gpu: bool = False,
    callback: Optional[Callable[[str], None]] = None,
) -> ProcessingResult:
    """Black formatiert automatisch komplexe Signaturen."""
    pass
```

### Dictionary und Listen
```python
# ✅ Black-Standard: Trailing Commas
config = {
    "video_settings": {
        "resolution": "1920x1080",
        "fps": 30,
        "codec": "h264",
    },
    "audio_settings": {
        "bitrate": 128,
        "channels": 2,
        "sample_rate": 44100,
    },
    "processing_options": [
        "frame_extraction",
        "object_detection",
        "face_recognition",
        "nsfw_detection",
    ],
}
```

### Comprehensions und Lambda
```python
# ✅ Black-Standard: Automatische Formatierung
filtered_results = [
    result.data
    for result in processing_results
    if result.confidence > 0.8 and result.status == "success"
]

# Lambda in komplexen Strukturen
sorted_videos = sorted(
    video_list,
    key=lambda x: (x.priority, x.created_at),
    reverse=True,
)
```

## Advanced Black Features

### Magic Comments
```python
# Temporäre Deaktivierung (selten verwenden!)
# fmt: off
manually_formatted_data = [
    [1,  2,  3,  4],
    [5,  6,  7,  8],
    [9, 10, 11, 12]
]
# fmt: on

# Einzelne Zeile überspringen
matrix = [[1, 2], [3, 4]]  # fmt: skip
```

### String-Handling
```python
# ✅ Black automatische String-Formatierung
long_message = (
    "Dies ist eine sehr lange Nachricht, die automatisch "
    "von Black in mehrere Zeilen aufgeteilt wird, um die "
    "88-Zeichen-Grenze einzuhalten."
)

# Multiline Strings bleiben unverändert
sql_query = """
    SELECT video_id, analysis_result, confidence
    FROM video_analysis
    WHERE confidence > 0.8
    AND status = 'completed'
    ORDER BY created_at DESC
"""
```

## Pre-commit Hook Details

### .pre-commit-config.yaml - Black Section
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.2.0
    hooks:
      - id: black
        language_version: python3.11
        args: [--target-version=py311]
        exclude: ^(migrations/|legacy_code/)

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]
        exclude: ^(migrations/|legacy_code/)
```

### Installation und Setup
```bash
# Einmalige Installation
pip install pre-commit black isort
pre-commit install

# Manuelle Ausführung auf allen Dateien
pre-commit run black --all-files
pre-commit run isort --all-files
```

## Makefile Integration

### Black-spezifische Targets
```makefile
.PHONY: black isort format-black check-black

black: ## Formatiert Code mit Black
	@echo "🎨 Formatiere mit Black..."
	python -m black services/ tests/ scripts/

isort: ## Sortiert Imports mit isort
	@echo "🔧 Sortiere Imports..."
	python -m isort services/ tests/ scripts/ --profile black

check-black: ## Prüft Black-Formatierung ohne Änderungen
	@echo "🔍 Prüfe Black-Formatierung..."
	python -m black --check --diff services/ tests/ scripts/
	python -m isort --check-only --diff services/ tests/ scripts/

format-black: black isort ## Vollständige Black-Formatierung
	@echo "✅ Black-Formatierung abgeschlossen"
```

## CI/CD - Black-spezifische Pipeline

### GitHub Actions - Black Only
```yaml
name: Black Standard Check
on: [push, pull_request]

jobs:
  black-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Black and isort
        run: |
          pip install black==24.2.0 isort==5.13.2

      - name: Check Black formatting
        run: |
          black --check --diff services/ tests/ scripts/

      - name: Check import sorting
        run: |
          isort --check-only --diff services/ tests/ scripts/ --profile black

      - name: Format report on failure
        if: failure()
        run: |
          echo "❌ Black-Standard-Verstoß gefunden!"
          echo "🔧 Führe 'make format-black' aus, um zu beheben"
```

## IDE-spezifische Black-Integration

### VS Code - Detaillierte Settings
```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--target-version", "py311",
        "--line-length", "88"
    ],
    "python.formatting.blackPath": "./venv/bin/black",
    "editor.formatOnSave": true,
    "editor.formatOnPaste": false,
    "editor.formatOnType": false,
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### PyCharm - Black Tool Configuration
```
File → Settings → Tools → External Tools

Name: Black Format
Program: $ProjectFileDir$/venv/bin/black
Arguments: $FilePath$ --target-version py311
Working Directory: $ProjectFileDir$
```

## Monitoring und Compliance

### Black-Compliance-Metriken
```bash
# Black-spezifische Reports
black --check services/ tests/ scripts/ 2>&1 | grep "files" || echo "Alle Dateien Black-konform"

# Detaillierter Diff-Report
black --check --diff services/ > black_violations.diff

# Line-Length-Violations
grep -r "# noqa: E501\|# pylint: disable=line-too-long" services/ || echo "Keine Line-Length-Exceptions"
```

### Automatisierte Black-Updates
```bash
# Black-Version-Update-Workflow
pip install --upgrade black
black --check services/ tests/ scripts/ || (
    echo "Black-Update erfordert Reformatierung"
    black services/ tests/ scripts/
    git add -A
    git commit -m "style: update to new Black version"
)
```

## Legacy-Code Migration Strategy

### Schritt-für-Schritt Black-Migration
```bash
# 1. Service-spezifische Migration
black services/llm_service/
git add services/llm_service/
git commit -m "style: format llm_service with Black"

# 2. Test-Migration
black tests/unit/test_llm_service/
git add tests/unit/test_llm_service/
git commit -m "style: format llm_service tests with Black"

# 3. Integration-Migration
black tests/integration/
git add tests/integration/
git commit -m "style: format integration tests with Black"
```

### Konflikt-Resolution bei Black-Updates
```bash
# Merge-Konflikte durch Black-Formatierung lösen
git checkout feature-branch
make format-black
git add -A
git commit -m "style: resolve Black formatting conflicts"
git rebase main
```

---

## 🔗 Integration mit Master-Regelwerk

Diese detaillierte Black-Standard-Regel ist Teil des **Master-Formatierungsregelwerks** (`.cursorrules.formatting`).

**Für allgemeine Formatierung siehe**: `.cursorrules.formatting`
**Für umfassende Regeln siehe**: `.cursorrules/README.md`

**Verwandte Regeln:**
- **Linter-Compliance**: `.cursorrules/rules/linter_compliance.md`
- **Feature-Testing**: `.cursorrules/rules/feature_testing.md`
- **Config-Validation**: `.cursorrules/rules/config_validation.md`

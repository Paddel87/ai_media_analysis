# AI Media Analysis System - Konfigurationsdatei-Validierung Regel
# Version: 1.0.0
# Status: Aktiv - OBLIGATORISCH für alle Konfigurationsdateien

## Konfigurationsdatei-Validierungs-Philosophie
- **Konsistenz**: Einheitliche Konfiguration im gesamten Projekt
- **Validierung**: Automatische Syntax- und Duplikatsprüfung
- **Prävention**: Fehler durch ungültige Konfiguration verhindern
- **Automatisierung**: Validierung in CI/CD-Pipeline integriert
- **Wartbarkeit**: Zentrale Konfigurationsverwaltung

## Obligatorische Konfigurationsdatei-Anforderungen

### 1. Keine Duplikate erlaubt (PFLICHT)
- **Duplikat-Detektion**: Automatische Erkennung doppelter Einträge
- **Syntax-Validierung**: Korrekte INI/TOML/YAML-Syntax
- **Key-Eindeutigkeit**: Jeder Konfigurationsschlüssel nur einmal pro Sektion
- **Cross-File-Konsistenz**: Übereinstimmung zwischen verschiedenen Konfigurationsdateien

### 2. Unterstützte Konfigurationsdateien
```
pytest.ini           # Test-Konfiguration
pyproject.toml        # Python-Projekt-Konfiguration
setup.cfg             # Setup-Tools-Konfiguration
.pre-commit-config.yaml  # Pre-commit-Hooks
docker-compose.yml    # Container-Orchestrierung
Makefile             # Build-Targets
.env.example         # Umgebungsvariablen-Template
requirements*.txt    # Python-Dependencies
```

### 3. Validierungsregeln nach Dateityp

#### pytest.ini Validierung
```ini
# ✅ KORREKT - Keine Duplikate
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test* *Tests
python_functions = test_* *_test

# ❌ FEHLER - Duplikate
[tool:pytest]
python_files = test_*.py
python_files = *_test.py  # DUPLIKAT!
```

#### pyproject.toml Validierung
```toml
# ✅ KORREKT - Eindeutige Sektionen
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"

# ❌ FEHLER - Doppelte Sektion
[tool.black]
line-length = 88
[tool.black]  # DUPLIKAT!
target-version = ['py311']
```

#### docker-compose.yml Validierung
```yaml
# ✅ KORREKT - Eindeutige Service-Namen
services:
  redis:
    image: redis:7-alpine
  vector-db:
    image: chromadb/chroma

# ❌ FEHLER - Doppelte Services
services:
  redis:
    image: redis:7-alpine
  redis:  # DUPLIKAT!
    image: redis:6-alpine
```

### 4. Automatische Validierungs-Tools

#### Config Validator Script
```python
#!/usr/bin/env python3
"""
Konfigurationsdatei-Validator für AI Media Analysis System.
Erkennt Duplikate, Syntaxfehler und Inkonsistenzen.
"""

import configparser
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import tomli
import yaml


class ConfigValidator:
    """Validator für verschiedene Konfigurationsdateien."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_pytest_ini(self) -> bool:
        """Validiert pytest.ini auf Duplikate und Syntax."""
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            return True

        try:
            config = configparser.ConfigParser()
            config.read(pytest_ini)

            # Check for duplicate keys in sections
            with open(pytest_ini) as f:
                content = f.read()

            for section_name in config.sections():
                section_lines = []
                in_section = False
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith(f'[{section_name}]'):
                        in_section = True
                        continue
                    elif line.startswith('[') and in_section:
                        break
                    elif in_section and '=' in line:
                        key = line.split('=')[0].strip()
                        if key in section_lines:
                            self.errors.append(
                                f"pytest.ini: Duplicate key '{key}' in section [{section_name}]"
                            )
                        section_lines.append(key)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"pytest.ini: Syntax error - {e}")
            return False

    def validate_pyproject_toml(self) -> bool:
        """Validiert pyproject.toml auf Duplikate und Syntax."""
        pyproject_toml = self.project_root / "pyproject.toml"
        if not pyproject_toml.exists():
            return True

        try:
            with open(pyproject_toml, 'rb') as f:
                data = tomli.load(f)

            # Check for required sections
            required_sections = ['tool.black', 'tool.isort', 'tool.pytest.ini_options']
            for section_path in required_sections:
                current = data
                for key in section_path.split('.'):
                    if key not in current:
                        self.warnings.append(
                            f"pyproject.toml: Missing recommended section [{section_path}]"
                        )
                        break
                    current = current[key]

            return True

        except Exception as e:
            self.errors.append(f"pyproject.toml: Syntax error - {e}")
            return False

    def validate_docker_compose(self) -> bool:
        """Validiert docker-compose.yml auf doppelte Services."""
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            return True

        try:
            with open(compose_file) as f:
                data = yaml.safe_load(f)

            services = data.get('services', {})
            service_names = list(services.keys())
            unique_services = set(service_names)

            if len(service_names) != len(unique_services):
                duplicates = [name for name in unique_services
                            if service_names.count(name) > 1]
                for dup in duplicates:
                    self.errors.append(
                        f"docker-compose.yml: Duplicate service '{dup}'"
                    )

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"docker-compose.yml: Syntax error - {e}")
            return False

    def validate_all(self) -> bool:
        """Führt alle Validierungen durch."""
        results = [
            self.validate_pytest_ini(),
            self.validate_pyproject_toml(),
            self.validate_docker_compose(),
        ]

        return all(results)

    def report(self) -> None:
        """Gibt Validierungsergebnisse aus."""
        if self.errors:
            print("❌ Konfigurationsfehler gefunden:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("⚠️  Konfigurationswarnungen:")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("✅ Alle Konfigurationsdateien sind gültig")


if __name__ == "__main__":
    validator = ConfigValidator()
    is_valid = validator.validate_all()
    validator.report()
    sys.exit(0 if is_valid else 1)
```

### 5. Pre-commit Hook Integration
```yaml
# .pre-commit-config.yaml - Config Validation
repos:
  - repo: local
    hooks:
      - id: config-validator
        name: Validate Configuration Files
        entry: python scripts/validate_config.py
        language: system
        files: \.(ini|toml|yml|yaml|cfg)$
        pass_filenames: false

  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        args: [-c=.yamllint.yml]

  - repo: https://github.com/python-jsonschema/check-jsonschema
    rev: 0.28.0
    hooks:
      - id: check-github-workflows
```

### 6. Makefile-Integration
```makefile
# Config Validation Targets
validate-config: ## Validiert alle Konfigurationsdateien
	@echo "🔍 Validiere Konfigurationsdateien..."
	python scripts/validate_config.py
	@echo "✅ Konfigurationsvalidierung abgeschlossen"

check-pytest-ini: ## Spezielle pytest.ini Validierung
	@echo "🧪 Validiere pytest.ini..."
	python -c "import configparser; c=configparser.ConfigParser(); c.read('pytest.ini'); print('✅ pytest.ini syntax OK')"
	@python scripts/check_pytest_duplicates.py

check-pyproject: ## Validiert pyproject.toml
	@echo "📦 Validiere pyproject.toml..."
	python -c "import tomli; tomli.load(open('pyproject.toml', 'rb')); print('✅ pyproject.toml syntax OK')"

check-docker-compose: ## Validiert docker-compose.yml
	@echo "🐳 Validiere docker-compose.yml..."
	docker-compose config --quiet
	@echo "✅ docker-compose.yml syntax OK"

fix-config: ## Automatische Konfigurationsreparatur (wo möglich)
	@echo "🔧 Repariere Konfigurationsdateien..."
	python scripts/fix_config_duplicates.py
	@echo "✅ Konfigurationsreparatur abgeschlossen"
```

### 7. GitHub Actions Integration
```yaml
# .github/workflows/config-validation.yml
name: Configuration Validation
on: [push, pull_request]

jobs:
  validate-config:
    name: Validate Configuration Files
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install validation tools
        run: |
          pip install tomli pyyaml

      - name: Validate pytest.ini
        run: |
          echo "🧪 Validating pytest.ini..."
          python scripts/validate_config.py pytest

      - name: Validate pyproject.toml
        run: |
          echo "📦 Validating pyproject.toml..."
          python scripts/validate_config.py pyproject

      - name: Validate docker-compose.yml
        run: |
          echo "🐳 Validating docker-compose.yml..."
          docker-compose config --quiet

      - name: Full config validation
        run: |
          echo "🔍 Running full configuration validation..."
          python scripts/validate_config.py --all

      - name: Fail on validation errors
        run: |
          if [ -f "config_errors.log" ]; then
            echo "❌ Configuration validation failed!"
            cat config_errors.log
            exit 1
          fi
```

## Spezifische Reparatur-Strategien

### pytest.ini Duplikat-Reparatur
```python
def fix_pytest_ini_duplicates():
    """Repariert doppelte Einträge in pytest.ini"""
    config = configparser.ConfigParser()
    config.read('pytest.ini')

    # Merge duplicate keys
    fixed_config = configparser.ConfigParser()

    for section_name in config.sections():
        if not fixed_config.has_section(section_name):
            fixed_config.add_section(section_name)

        # Collect all values for duplicate keys
        key_values = {}
        for key, value in config.items(section_name):
            if key in key_values:
                # Merge values
                existing = key_values[key].split()
                new_values = value.split()
                merged = list(set(existing + new_values))
                key_values[key] = ' '.join(merged)
            else:
                key_values[key] = value

        # Write merged values
        for key, value in key_values.items():
            fixed_config.set(section_name, key, value)

    # Write fixed config
    with open('pytest.ini', 'w') as f:
        fixed_config.write(f)
```

### Konfigurationsdateien-Konsistenz
```python
def check_config_consistency():
    """Prüft Konsistenz zwischen verschiedenen Konfigurationsdateien"""

    # Black line-length consistency
    pyproject_black = get_black_line_length_from_pyproject()
    pytest_black = get_black_line_length_from_pytest()

    if pyproject_black != pytest_black:
        print(f"⚠️ Black line-length mismatch: pyproject.toml={pyproject_black}, pytest.ini={pytest_black}")

    # Python version consistency
    pyproject_python = get_python_version_from_pyproject()
    dockerfile_python = get_python_version_from_dockerfile()

    if pyproject_python != dockerfile_python:
        print(f"⚠️ Python version mismatch: pyproject.toml={pyproject_python}, Dockerfile={dockerfile_python}")
```

## Monitoring und Alerting

### Konfigurationsdrift-Erkennung
```bash
# Wöchentlicher Config-Health-Check
config-health-check: ## Umfassende Konfigurationsprüfung
	@echo "🏥 Konfiguration Health Check..."
	@python scripts/validate_config.py --comprehensive
	@python scripts/check_config_drift.py
	@echo "📊 Config Health Report generiert"
```

### Automatisierte Reports
```python
def generate_config_report():
    """Generiert umfassenden Konfigurationsbericht"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "files_checked": [],
        "errors_found": [],
        "warnings_found": [],
        "consistency_checks": {},
        "recommendations": []
    }

    # Validiere alle Konfigurationsdateien
    validator = ConfigValidator()
    validator.validate_all()

    report["errors_found"] = validator.errors
    report["warnings_found"] = validator.warnings

    # Schreibe Report
    with open("reports/config-health.json", "w") as f:
        json.dump(report, f, indent=2)
```

## Integration mit anderen Regeln

### Feature Testing Integration
- Test-Konfiguration muss valide sein
- Coverage-Konfiguration wird validiert
- Test-Discovery-Patterns werden geprüft

### Black Standard Integration
- Black-Konfiguration wird auf Konsistenz geprüft
- Line-length-Einstellungen müssen übereinstimmen
- Target-Python-Versionen werden abgeglichen

### Iterative Development Integration
- Service-Konfigurationen werden validiert
- Docker-Compose-Service-Namen werden geprüft
- Environment-Variable-Konsistenz

## Developer-Workflow

### Vor jeder Konfigurationsänderung
```bash
# 1. Aktuelle Konfiguration validieren
make validate-config

# 2. Änderungen vornehmen
# ... edit config files ...

# 3. Erneut validieren
make validate-config

# 4. Bei Fehlern automatisch reparieren (wo möglich)
make fix-config

# 5. Commit mit Validierung
git add .
git commit -m "Config update: Description"
```

### IDE-Integration
```json
// VS Code tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Validate Config",
            "type": "shell",
            "command": "make validate-config",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        }
    ]
}
```

## Troubleshooting Guide

### Häufige Probleme

#### pytest.ini Duplikate
```bash
# Problem identifizieren
grep -n "python_files" pytest.ini

# Automatisch reparieren
python scripts/fix_pytest_duplicates.py

# Manuell reparieren
# Entferne doppelte Zeilen und merge Werte
```

#### pyproject.toml Syntax-Fehler
```bash
# Syntax validieren
python -c "import tomli; tomli.load(open('pyproject.toml', 'rb'))"

# Häufige Probleme:
# - Fehlende Anführungszeichen bei Strings
# - Falsche Array-Syntax
# - Ungültige TOML-Struktur
```

#### docker-compose.yml Service-Duplikate
```bash
# Service-Namen prüfen
docker-compose config --services | sort | uniq -d

# Duplikate entfernen und Services zusammenführen
```

---

## 🎯 Status: SOFORT AKTIV

Diese Regel ist **sofort wirksam** und gilt für:
- ✅ Alle Konfigurationsdateien
- ✅ Neue und geänderte Konfigurationen
- ✅ CI/CD Pipeline-Validierung
- ✅ Pre-commit-Hook-Überprüfung
- ✅ Code Review Requirements

**Keine ungültigen Konfigurationsdateien mehr!** 🔧✨

---

*Diese Regel ergänzt:*
- Black-Standard-Regel (Formatierung)
- Feature-Testing-Regel (Test-Konfiguration)
- Iterative-Development-Regel (Service-Konfiguration)

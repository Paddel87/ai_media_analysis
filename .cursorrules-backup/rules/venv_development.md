# Entwicklungsumgebung – venv-Projektregel

## 🎯 Zweck
Die gesamte Entwicklung erfolgt ausschließlich innerhalb eines aktivierten Python `venv` zur Sicherstellung reproduzierbarer Umgebungen, eindeutiger Abhängigkeitsauflösungen und vollständiger Kompatibilität.

## 📋 Verbindliche Anforderungen

### 1. **venv-Aktivierung (VERPFLICHTEND)**
- **Bei Projektstart**: `python -m venv .venv && .venv\Scripts\activate` (Windows)
- **Bei Projektstart**: `python -m venv .venv && source .venv/bin/activate` (Linux/macOS)
- **Alle Entwicklungstätigkeiten** erfolgen nur im aktivierten venv
- **IDE/Cursor** muss venv als Python-Interpreter verwenden

### 2. **Paket-Installation (NUR IM VENV)**
- **Alle pip-Installationen** nur im aktivierten venv
- **Entwicklungs-Dependencies**: `pip install -r requirements/development.txt`
- **Test-Dependencies**: `pip install -r requirements/testing.txt`
- **Service-Dependencies**: Nach Bedarf aus `requirements/services/`

### 3. **venv-Verzeichnis-Struktur**
```
.venv/                    # Virtual Environment (in .gitignore)
├── Scripts/             # Windows Aktivierungs-Scripts
│   ├── activate         # Aktivierungs-Script
│   ├── deactivate       # Deaktivierungs-Script
│   └── python.exe       # venv Python-Interpreter
├── Lib/                 # Python-Bibliotheken
└── pyvenv.cfg          # venv-Konfiguration
```

### 4. **Environment-Isolation**
- **Keine System-Python-Pakete** verwenden
- **Vollständige Isolation** von globalen Installationen
- **Reproduzierbare Umgebung** für alle Entwickler
- **Konsistente Tool-Versionen** (Black, pytest, etc.)

## 🚦 venv-Management-Workflow

### **Erstes Setup**
```bash
# 1. venv erstellen
python -m venv .venv

# 2. venv aktivieren (Windows)
.venv\Scripts\activate

# 3. pip aktualisieren
python -m pip install --upgrade pip

# 4. Basis-Dependencies installieren
pip install -r requirements/development.txt

# 5. Makefile-Targets verwenden
make venv-setup
```

### **Täglicher Workflow**
```bash
# 1. venv aktivieren
.venv\Scripts\activate

# 2. Dependencies-Status prüfen
make venv-check

# 3. Entwicklung durchführen
# ... Code-Änderungen ...

# 4. Tests im venv ausführen
make test

# 5. venv deaktivieren (optional)
deactivate
```

### **Dependency-Management**
```bash
# Dependencies hinzufügen
pip install neue-bibliothek
pip freeze > requirements/development.txt

# Dependencies aktualisieren
pip install --upgrade -r requirements/development.txt

# Dependencies synchronisieren
make venv-sync
```

## 🔧 Automatisierung

### **Makefile-Integration**
```bash
# venv-Setup und Aktivierung
make venv-setup          # Erstellt und konfiguriert venv
make venv-activate       # Aktiviert venv
make venv-check          # Überprüft venv-Status
make venv-clean          # Löscht und erstellt venv neu
make venv-sync           # Synchronisiert Dependencies

# Development mit venv
make venv-install-dev    # Installiert Development-Dependencies
make venv-install-test   # Installiert Test-Dependencies
make venv-install-all    # Installiert alle Dependencies

# venv-Validierung
make venv-validate       # Validiert venv-Umgebung
make venv-requirements   # Generiert requirements.txt
```

### **Automatische Scripts**
- **`scripts/venv_setup.py`**: Automatisches venv-Setup
- **`scripts/venv_check.py`**: venv-Status-Überprüfung
- **`scripts/venv_requirements.py`**: Requirements-Management

### **IDE-Integration (Cursor)**
```json
// .vscode/settings.json
{
    "python.pythonPath": ".venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackPath": ".venv/Scripts/black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestPath": ".venv/Scripts/pytest"
}
```

## 📊 venv-Compliance-Checks

### **Automatische Validierung**
```python
# Prüft ob venv aktiviert ist
import sys
import os

def check_venv_active():
    """Überprüft ob venv aktiviert ist."""
    if not hasattr(sys, 'real_prefix') and not (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    ):
        raise EnvironmentError(
            "❌ venv nicht aktiviert! "
            "Führe '.venv\\Scripts\\activate' aus."
        )
    print("✅ venv ist aktiviert")
```

### **CI/CD-Integration**
```yaml
# GitHub Actions venv-Setup
- name: 🐍 Setup Python venv
  run: |
    python -m venv .venv
    .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements/testing.txt
```

### **venv-Status-Monitoring**
- **Pre-commit Hook**: Überprüft venv-Aktivierung
- **Makefile-Targets**: Validieren venv vor jeder Operation
- **IDE-Warnings**: Warnung bei System-Python-Verwendung

## 🚨 Enforcement-Strategie

### **Automatische Checks**
1. **Pre-commit Hook**: Blockiert Commits ohne aktives venv
2. **Makefile-Guards**: Alle Targets prüfen venv-Status
3. **Script-Validation**: Python-Scripts validieren venv automatisch
4. **CI/CD-Gates**: GitHub Actions verwenden venv verpflichtend

### **Development-Guards**
```bash
# Alle Makefile-Targets starten mit venv-Check
@if [ -z "$$VIRTUAL_ENV" ]; then \
    echo "❌ venv nicht aktiviert! Führe 'source .venv/bin/activate' aus"; \
    exit 1; \
fi
```

### **Error-Handling**
- **Fehlende venv-Aktivierung**: Automatische Hilfe-Nachrichten
- **Falsche Python-Version**: Automatische Korrektur-Vorschläge
- **Dependencies-Konflikt**: Automatische Synchronisations-Tools

## 🛠️ Troubleshooting

### **Häufige Probleme**

#### **venv nicht aktiviert**
```bash
# Problem: Command not found oder falsche Python-Version
# Lösung:
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

#### **venv existiert nicht**
```bash
# Problem: .venv Verzeichnis fehlt
# Lösung:
make venv-setup
# oder
python -m venv .venv
```

#### **Dependencies-Konflikte**
```bash
# Problem: Paket-Versionen inkompatibel
# Lösung:
make venv-clean && make venv-setup
# oder
pip install --force-reinstall -r requirements/development.txt
```

#### **IDE erkennt venv nicht**
```bash
# Problem: Cursor/VS Code verwendet System-Python
# Lösung:
# 1. Cursor: Python Interpreter auswählen → .venv/Scripts/python.exe
# 2. settings.json aktualisieren
# 3. Cursor neu starten
```

### **venv-Reparatur**
```bash
# Komplette venv-Neuerstellung
make venv-clean-rebuild

# Dependencies neu installieren
make venv-reinstall-deps

# venv-Validierung und Reparatur
make venv-repair
```

## 📋 Compliance-Checklist

### **Entwickler-Checklist**
- [ ] `.venv` ist erstellt und aktiviert
- [ ] Cursor verwendet `.venv/Scripts/python.exe` als Interpreter
- [ ] Alle pip-Installationen erfolgen im venv
- [ ] `requirements.txt` ist aktuell
- [ ] Tests laufen im venv ohne Fehler
- [ ] Linting-Tools verwenden venv-Installationen

### **Projekt-Setup-Checklist**
- [ ] `.venv/` ist in `.gitignore` eingetragen
- [ ] `requirements/` Struktur ist korrekt
- [ ] Makefile-Targets funktionieren mit venv
- [ ] CI/CD verwendet venv-Setup
- [ ] Dokumentation beschreibt venv-Workflow

### **Team-Onboarding-Checklist**
- [ ] Neue Entwickler: venv-Setup-Anleitung befolgt
- [ ] IDE-Konfiguration: venv-Integration eingerichtet
- [ ] Workflow-Training: venv-Management verstanden
- [ ] Troubleshooting: Häufige Probleme bekannt

## 🔄 Dependency-Management

### **Requirements-Struktur**
```
requirements/
├── base.txt              # Basis-Production-Dependencies
├── development.txt       # Development-Tools (Black, isort, etc.)
├── testing.txt          # Test-Framework (pytest, coverage, etc.)
└── services/            # Service-spezifische Dependencies
    ├── llm.txt          # LLM-Service Dependencies
    ├── vision.txt       # Computer Vision Dependencies
    └── cloud.txt        # Cloud Storage Dependencies
```

### **Requirements-Updates**
```bash
# Aktuelle Requirements erfassen
pip freeze > requirements/current.txt

# Dependencies aktualisieren
pip install --upgrade -r requirements/development.txt

# Security-Updates prüfen
pip-audit

# Outdated packages finden
pip list --outdated
```

### **Version-Pinning-Strategie**
- **Production**: Exakte Versionen (`package==1.2.3`)
- **Development**: Kompatible Versionen (`package>=1.2.0,<2.0.0`)
- **Testing**: Aktuelle stabile Versionen
- **Security**: Immer neueste Patches

## 📚 Best Practices

### **venv-Naming-Konventionen**
- **Standard**: `.venv` (empfohlen für Projektverzeichnis)
- **Alternative**: `.venv-ai-media` (bei mehreren Projekten)
- **Temporär**: `.venv-test` (für experimentelle Setups)

### **Performance-Optimierung**
- **pip-Cache**: Verwende `pip install --cache-dir .pip-cache`
- **Parallel-Installation**: `pip install --use-feature=parallel`
- **Local-Index**: Für wiederkehrende Dependencies

### **Security-Considerations**
- **pip-audit**: Regelmäßige Vulnerability-Scans
- **Hash-Checking**: `pip install --require-hashes`
- **Trusted-Hosts**: Nur vertrauenswürdige PyPI-Mirrors

### **Cross-Platform-Kompatibilität**
```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# PowerShell
.venv\Scripts\Activate.ps1

# Universal-Script (scripts/activate_venv.py)
python scripts/activate_venv.py
```

## 🆘 Support und Hilfe

### **venv-Hilfe-Commands**
```bash
make venv-help           # Zeigt venv-Befehle an
make venv-status         # Zeigt venv-Status an
make venv-info           # Zeigt venv-Informationen an
make venv-doctor         # Diagnose-Tool für venv-Probleme
```

### **Automatische Diagnose**
```python
# scripts/venv_doctor.py
def diagnose_venv():
    """Automatische venv-Diagnose"""
    checks = [
        check_venv_exists(),
        check_venv_activated(),
        check_python_version(),
        check_pip_version(),
        check_dependencies(),
        check_ide_integration()
    ]
    return all(checks)
```

### **Community-Support**
- **Interne Dokumentation**: `docs/venv-guide.md`
- **FAQ**: Häufige venv-Probleme und Lösungen
- **Video-Tutorials**: venv-Setup für neue Teammitglieder
- **Slack-Channel**: `#venv-support` für schnelle Hilfe

## 🔍 Monitoring und Metrics

### **venv-Health-Monitoring**
- **Daily Check**: Automatische venv-Validierung
- **Dependency-Drift**: Überwachung von Requirements-Änderungen
- **Security-Scan**: Wöchentliche Vulnerability-Checks
- **Performance-Metrics**: Installation-Zeiten und Größe

### **Compliance-Metrics**
- **venv-Adoption-Rate**: % der Entwickler mit korrektem venv-Setup
- **Dependency-Consistency**: Übereinstimmung zwischen Umgebungen
- **Issue-Resolution-Time**: Zeit zur Lösung venv-bedingter Probleme
- **CI/CD-Success-Rate**: venv-bedingte Build-Failures

---

**Status**: ✅ AKTIV
**Letzte Aktualisierung**: 2025-01-06
**Nächste Review**: 2025-02-06
**Verantwortlich**: Development Team
**Priority**: 🔴 CRITICAL
**Enforcement**: 🚨 VERPFLICHTEND

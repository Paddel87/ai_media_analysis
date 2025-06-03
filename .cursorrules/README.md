# AI Media Analysis System - Cursor Rules Übersicht
# Version: 3.0.0 - Bereinigt und Strukturiert
# Status: Master-Index für alle Entwicklungsregeln

## 🎯 REGEL-HIERARCHIE

### 📁 Root-Level Master-Regeln
- **`.cursorrules.formatting`** - Master-Formatierungsregel (verweist auf detaillierte Regeln)
- **`.cursorrules.docs`** - Dokumentations-Standards und Living Documentation
- **`.cursorrules.cloud`** - Cloud AI-Integration und Async Processing
- **`.cursorrules.vps`** - VPS-Optimierung und Resource Management

### 📂 Detaillierte Regeln (`.cursorrules/rules/`)
1. **`black_standard.md`** - Strenge Black-Code-Formatierung (OBLIGATORISCH)
2. **`linter_compliance.md`** - Vollständige Linter-Integration (flake8, mypy, bandit)
3. **`feature_testing.md`** - Umfassende Test-Standards und TDD-Praktiken
4. **`config_validation.md`** - Konfigurations-Validierung und Schema-Enforcement
5. **`venv_development.md`** - Virtual Environment und Dependency Management
6. **`iterative_development.md`** - 4-Iterations-Entwicklungsmodell

---

## 🚀 QUICK START GUIDE

### Für neue Entwickler
```bash
# 1. Pre-commit Hooks installieren
make pre-commit-install

# 2. Alle Regeln anwenden
make check-all

# 3. Code automatisch formatieren
make format

# 4. Tests ausführen
make test
```

### Für bestehende Projekte
```bash
# 1. Formatierung migrieren
make format-all

# 2. Linter-Compliance prüfen
make lint

# 3. Konfiguration validieren
make config-validate

# 4. Test-Coverage prüfen
make test-coverage
```

---

## 📋 REGEL-MATRIX

| Regel | Status | Enforcement | Auto-Fix | CI/CD |
|-------|--------|-------------|----------|-------|
| **Black-Standard** | ✅ Obligatorisch | Pre-commit + CI | ✅ Auto | ✅ Blockiert |
| **Linter-Compliance** | ✅ Obligatorisch | CI/CD | ⚠️ Partial | ✅ Blockiert |
| **Feature-Testing** | ✅ Obligatorisch | CI/CD | ❌ Manual | ✅ Blockiert |
| **Config-Validation** | ✅ Obligatorisch | Pre-commit | ✅ Auto | ✅ Blockiert |
| **Venv-Development** | ✅ Obligatorisch | Local | ⚠️ Semi | ⚠️ Warning |
| **Iterative-Development** | 📋 Prozess | Review | ❌ Manual | ❌ None |

---

## 🔧 ENTWICKLUNGSWORKFLOW

### 1. **Setup Phase**
```bash
# Virtual Environment aktivieren
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
make install-dev

# Pre-commit Hooks setup
make pre-commit-install
```

### 2. **Development Phase**
```bash
# Feature Branch erstellen
git checkout -b feature/neue-funktion

# Code entwickeln (automatische Formatierung)
# ... entwickeln ...

# Alle Checks ausführen
make check-all

# Commit (Pre-commit Hooks laufen automatisch)
git commit -m "feat: neue Funktion implementiert"
```

### 3. **Testing Phase**
```bash
# Unit Tests
make test

# Integration Tests
make test-integration

# Coverage Report
make test-coverage

# Performance Tests
make test-performance
```

### 4. **Review Phase**
```bash
# Pre-Review Checks
make check-all

# Pull Request erstellen
# CI/CD läuft automatisch alle Regel-Checks
```

---

## 🎨 FORMATIERUNGS-STACK

### Automatische Tools
```yaml
# Pre-commit Pipeline
1. Black          # Code-Formatierung
2. isort          # Import-Sortierung
3. flake8         # Style-Linting
4. mypy           # Type-Checking
5. bandit         # Security-Scanning
6. safety         # Dependency-Security
7. yamllint       # YAML-Validation
8. json-schema    # JSON-Validation
```

### Manuelle Reviews
- **Code-Logic**: Funktionale Korrektheit
- **Architecture**: Design-Patterns und Struktur
- **Documentation**: Vollständigkeit und Klarheit
- **Testing**: Test-Coverage und Qualität

---

## 🔍 QUALITY GATES

### Automatische Gates (CI/CD)
- ✅ **Format-Check**: 100% Black-Compliance
- ✅ **Import-Check**: 100% isort-Compliance
- ✅ **Lint-Check**: Null flake8-Violations
- ✅ **Type-Check**: Null mypy-Errors
- ✅ **Security-Check**: Null bandit-Issues
- ✅ **Test-Check**: >90% Coverage
- ✅ **Config-Check**: Schema-Validation

### Manuelle Gates (Review)
- 📋 **Feature-Completeness**: Vollständige Implementation
- 📋 **Test-Quality**: Aussagekräftige Tests
- 📋 **Documentation**: Aktualisierte Docs
- 📋 **Performance**: Keine Regression

---

## 📊 REGEL-COMPLIANCE MONITORING

### Tägliche Checks
```bash
# Quick Health Check
make health-check

# Format Compliance
make format-report

# Test Coverage
make coverage-report
```

### Wöchentliche Reports
```bash
# Vollständiger Quality Report
make quality-report

# Security Scan
make security-scan

# Dependency Audit
make deps-audit
```

### Monatliche Reviews
- 📈 **Compliance-Trends**: Verbesserung over Zeit
- 📈 **Tool-Effectiveness**: ROI der Automatisierung
- 📈 **Developer-Experience**: Entwickler-Feedback
- 📈 **Performance-Impact**: Build-Zeit-Trends

---

## 🚨 ENFORCEMENT LEVELS

### Level 1: **Pre-commit** (Lokale Entwicklung)
- ✅ Automatische Formatierung
- ⚠️ Warnungen bei Violations
- 🔧 Auto-Fix wo möglich

### Level 2: **CI/CD** (Pull Requests)
- ❌ Blockiert bei Critical Violations
- 📊 Detaillierte Reports
- 📋 Review-Kommentare

### Level 3: **Production** (Main Branch)
- 🚫 Strikte Enforcement
- 📈 Quality-Metrics-Tracking
- 🔔 Alert-System bei Degradation

---

## 🎯 EVOLUTION UND UPDATES

### Regel-Updates
1. **RFC-Prozess**: Änderungen werden diskutiert
2. **Pilot-Testing**: Neue Regeln werden getestet
3. **Gradueller Rollout**: Schrittweise Einführung
4. **Feedback-Integration**: Community-Input

### Tool-Updates
```bash
# Dependency Updates prüfen
make deps-check

# Tool-Version Updates
make tools-update

# Configuration Updates
make config-update
```

---

## 🔗 EXTERNE RESSOURCEN

### Dokumentation
- **Black**: https://black.readthedocs.io/
- **isort**: https://pycqa.github.io/isort/
- **flake8**: https://flake8.pycqa.org/
- **mypy**: https://mypy.readthedocs.io/
- **pytest**: https://docs.pytest.org/

### Best Practices
- **PEP 8**: Python Style Guide
- **PEP 484**: Type Hints
- **PEP 518**: Build System Requirements
- **PEP 621**: Project Metadata

---

## 🎪 ENTWICKLUNGSREGELN IMPLEMENTIERUNG

### ✅ **Implementiert und Aktiv**
- [x] Black-Standard-Compliance (100%)
- [x] Linter-Integration (flake8, mypy, bandit)
- [x] Feature-Testing-Framework (pytest)
- [x] Config-Validation (JSON/YAML-Schema)
- [x] Pre-commit-Hooks (Automatisierung)
- [x] CI/CD-Integration (GitHub Actions)

### 🚧 **In Arbeit**
- [ ] Performance-Benchmarking
- [ ] Advanced-Security-Scanning
- [ ] Documentation-Coverage-Tracking
- [ ] Advanced-Metrics-Dashboard

### 📋 **Geplant**
- [ ] AI-Code-Review-Integration
- [ ] Advanced-Refactoring-Automation
- [ ] Cross-Service-Dependency-Analysis
- [ ] Real-time-Quality-Monitoring

---

## 📞 SUPPORT UND HILFE

### Quick Help
```bash
# Regel-Übersicht anzeigen
make rules-help

# Spezifische Regel-Hilfe
make help-black        # Black-Standard
make help-testing      # Feature-Testing
make help-config       # Config-Validation
```

### Troubleshooting
- **Format-Probleme**: `make format-fix`
- **Import-Probleme**: `make imports-fix`
- **Test-Probleme**: `make test-debug`
- **Config-Probleme**: `make config-debug`

### Community
- **Issues**: GitHub Issues für Regel-Probleme
- **Discussions**: GitHub Discussions für Regel-Vorschläge
- **Wiki**: Detaillierte How-To-Guides

---

## 🏆 ENTWICKLUNGSREGELN STATUS

**🎯 Alpha 0.5.0: Enterprise Development Framework**
- ✅ 5 Hauptentwicklungsregeln implementiert
- ✅ Vollständige Automatisierung
- ✅ CI/CD-Integration
- ✅ Quality-Gates aktiv
- ✅ Developer-Experience optimiert

**🚀 Nächste Milestones:**
- 📋 Beta 0.6.0: Advanced-Analytics
- 📋 RC 0.7.0: AI-Integration
- 📋 v1.0.0: Production-Ready Framework

---

*Diese Regel-Sammlung bildet das Fundament für enterprise-grade Entwicklung im AI Media Analysis System. Alle Regeln sind aufeinander abgestimmt und arbeiten nahtlos zusammen für maximale Produktivität und Code-Qualität.*

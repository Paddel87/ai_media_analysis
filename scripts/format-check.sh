#!/bin/bash
# AI Media Analysis - Automatischer Formatierungs-Check
# Verwendung: ./scripts/format-check.sh [--fix]

set -e

echo "🎨 AI Media Analysis - Code-Formatierungs-Check"
echo "================================================"

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion für farbigen Output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Parameter prüfen
FIX_MODE=false
if [[ "$1" == "--fix" ]]; then
    FIX_MODE=true
    print_status "Formatierungs-Fix-Modus aktiviert"
fi

# Verzeichnisse definieren
PYTHON_DIRS="services tests"
ERROR_COUNT=0

print_status "Prüfe Python-Verzeichnisse: $PYTHON_DIRS"

# Black-Formatierung prüfen/fixieren
print_status "🖤 Black-Formatierung..."
if [[ "$FIX_MODE" == true ]]; then
    if python -m black $PYTHON_DIRS; then
        print_success "Black-Formatierung angewendet"
    else
        print_error "Black-Formatierung fehlgeschlagen"
        ((ERROR_COUNT++))
    fi
else
    if python -m black --check --diff $PYTHON_DIRS; then
        print_success "Black-Formatierung OK"
    else
        print_error "Black-Formatierung erforderlich - führe './scripts/format-check.sh --fix' aus"
        ((ERROR_COUNT++))
    fi
fi

# isort-Import-Sortierung prüfen/fixieren
print_status "🔧 isort-Import-Sortierung..."
if [[ "$FIX_MODE" == true ]]; then
    if python -m isort $PYTHON_DIRS; then
        print_success "isort-Sortierung angewendet"
    else
        print_error "isort-Sortierung fehlgeschlagen"
        ((ERROR_COUNT++))
    fi
else
    if python -m isort --check-only --diff $PYTHON_DIRS; then
        print_success "isort-Sortierung OK"
    else
        print_error "isort-Sortierung erforderlich - führe './scripts/format-check.sh --fix' aus"
        ((ERROR_COUNT++))
    fi
fi

# flake8-Linting (nur Check, keine Fixes)
print_status "🔍 flake8-Linting..."
if python -m flake8 $PYTHON_DIRS --max-line-length=88 --extend-ignore=E203,W503; then
    print_success "flake8-Linting OK"
else
    print_error "flake8-Linting Fehler gefunden"
    ((ERROR_COUNT++))
fi

# Trailing Whitespace prüfen/fixieren
print_status "🧹 Trailing Whitespace..."
if [[ "$FIX_MODE" == true ]]; then
    find $PYTHON_DIRS -name "*.py" -exec sed -i 's/[[:space:]]*$//' {} \;
    print_success "Trailing Whitespace entfernt"
else
    if find $PYTHON_DIRS -name "*.py" -exec grep -l '[[:space:]]$' {} \; | head -1 | grep -q .; then
        print_error "Trailing Whitespace gefunden - führe './scripts/format-check.sh --fix' aus"
        ((ERROR_COUNT++))
    else
        print_success "Trailing Whitespace OK"
    fi
fi

# End-of-File-Newline prüfen/fixieren
print_status "📄 End-of-File Newlines..."
if [[ "$FIX_MODE" == true ]]; then
    find $PYTHON_DIRS -name "*.py" -exec sh -c 'if [ "$(tail -c1 "$1")" != "" ]; then echo >> "$1"; fi' _ {} \;
    print_success "End-of-File Newlines korrigiert"
else
    FILES_WITHOUT_NEWLINE=$(find $PYTHON_DIRS -name "*.py" -exec sh -c 'if [ "$(tail -c1 "$1")" != "" ]; then echo "$1"; fi' _ {} \;)
    if [[ -n "$FILES_WITHOUT_NEWLINE" ]]; then
        print_error "Dateien ohne End-of-File Newline gefunden - führe './scripts/format-check.sh --fix' aus"
        ((ERROR_COUNT++))
    else
        print_success "End-of-File Newlines OK"
    fi
fi

# Zusammenfassung
echo ""
echo "================================================"
if [[ $ERROR_COUNT -eq 0 ]]; then
    print_success "🎉 Alle Formatierungs-Checks erfolgreich!"
    if [[ "$FIX_MODE" == true ]]; then
        print_status "Code wurde automatisch formatiert"
    fi
    exit 0
else
    print_error "❌ $ERROR_COUNT Formatierungs-Fehler gefunden!"
    if [[ "$FIX_MODE" == false ]]; then
        print_warning "Führe './scripts/format-check.sh --fix' aus um automatisch zu korrigieren"
    fi
    exit 1
fi 
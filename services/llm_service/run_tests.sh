#!/bin/bash

# Farben für die Ausgabe
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Funktion zum Ausführen der Tests
run_tests() {
    echo -e "${GREEN}Starte Tests...${NC}"
    
    # Unit Tests
    echo -e "\n${GREEN}Unit Tests:${NC}"
    pytest tests/ -v -m "not integration and not performance" --cov=. --cov-report=term-missing
    
    # Integration Tests
    echo -e "\n${GREEN}Integration Tests:${NC}"
    pytest tests/ -v -m "integration" --cov=. --cov-report=term-missing
    
    # Performance Tests
    echo -e "\n${GREEN}Performance Tests:${NC}"
    pytest tests/ -v -m "performance" --benchmark-only
    
    # Coverage Report
    echo -e "\n${GREEN}Coverage Report:${NC}"
    coverage report -m
    
    # HTML Report
    echo -e "\n${GREEN}Generiere HTML Report...${NC}"
    coverage html
    
    echo -e "\n${GREEN}Tests abgeschlossen!${NC}"
}

# Funktion zum Aufräumen
cleanup() {
    echo -e "\n${GREEN}Räume auf...${NC}"
    rm -rf .coverage
    rm -rf htmlcov
    rm -rf .pytest_cache
    rm -rf .benchmarks
}

# Hauptprogramm
main() {
    # Prüfe ob pytest installiert ist
    if ! command -v pytest &> /dev/null; then
        echo -e "${RED}pytest ist nicht installiert. Installiere Abhängigkeiten...${NC}"
        pip install -r requirements.txt
    fi
    
    # Führe Tests aus
    run_tests
    
    # Aufräumen
    cleanup
}

# Starte Hauptprogramm
main 
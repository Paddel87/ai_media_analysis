#!/usr/bin/env python3
"""
Feature Testing Regel Validierung
=====================================

Dieses Skript validiert, dass für alle Service-Dateien entsprechende Tests existieren.
Es wird als pre-commit Hook ausgeführt und blockiert Commits, wenn Tests fehlen.

Regel: Jede neue Service-Datei muss einen entsprechenden Test haben.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple
import re


def get_test_file_path(service_file: str) -> str:
    """
    Konvertiert einen Service-Dateipfad zu dem erwarteten Test-Dateipfad.

    Args:
        service_file: Pfad zur Service-Datei (z.B. "services/llm_service/main.py")

    Returns:
        Erwarteter Pfad zur Test-Datei (z.B. "tests/unit/services/llm_service/test_main.py")
    """
    # Entferne "services/" am Anfang und ersetze durch "tests/unit/services/"
    test_path = service_file.replace("services/", "tests/unit/services/", 1)

    # Konvertiere Dateiname zu Test-Dateiname
    path_parts = test_path.split("/")
    filename = path_parts[-1]

    if filename.endswith(".py"):
        # main.py -> test_main.py
        base_name = filename[:-3]  # Entferne .py
        test_filename = f"test_{base_name}.py"
        path_parts[-1] = test_filename

    return "/".join(path_parts)


def find_missing_tests(service_files: List[str]) -> List[Tuple[str, str]]:
    """
    Findet Service-Dateien, für die keine entsprechenden Tests existieren.

    Args:
        service_files: Liste von Service-Dateipfaden

    Returns:
        Liste von (service_file, expected_test_file) Tupeln für fehlende Tests
    """
    missing_tests: List[Tuple[str, str]] = []

    for service_file in service_files:
        # Überspringe __init__.py und bereits existierende Test-Dateien
        if service_file.endswith("__init__.py") or "test_" in service_file:
            continue

        expected_test_file = get_test_file_path(service_file)

        if not os.path.exists(expected_test_file):
            missing_tests.append((service_file, expected_test_file))

    return missing_tests


def check_test_quality(test_file: str) -> List[str]:
    """
    Prüft die Qualität einer Test-Datei.

    Args:
        test_file: Pfad zur Test-Datei

    Returns:
        Liste von Qualitätsproblemen
    """
    issues: List[str] = []

    if not os.path.exists(test_file):
        return ["Test-Datei existiert nicht"]

    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Prüfe auf Basis-Test-Strukturen
        if not re.search(r'def test_.*\(', content):
            issues.append("Keine Test-Funktionen gefunden")

        if not re.search(r'import pytest|from pytest', content):
            issues.append("pytest Import fehlt")

        if not re.search(r'""".*"""', content, re.DOTALL):
            issues.append("Docstrings fehlen")

        # Prüfe auf Assert-Statements
        if not re.search(r'assert ', content):
            issues.append("Keine Assert-Statements gefunden")

    except Exception as e:
        issues.append(f"Fehler beim Lesen der Test-Datei: {e}")

    return issues


def validate_test_coverage() -> bool:
    """
    Validiert die Test-Abdeckung für das gesamte Projekt.

    Returns:
        True wenn alle Anforderungen erfüllt sind, False sonst
    """
    # Finde alle Service-Dateien
    service_files: List[str] = []
    services_dir = Path("services")

    if services_dir.exists():
        for py_file in services_dir.rglob("*.py"):
            service_files.append(str(py_file))

    if not service_files:
        print("ℹ️  Keine Service-Dateien gefunden - Validierung übersprungen")
        return True

    # Prüfe auf fehlende Tests
    missing_tests = find_missing_tests(service_files)

    if missing_tests:
        print("❌ Feature Testing Regel verletzt!")
        print("")
        print("Die folgenden Service-Dateien haben keine entsprechenden Tests:")
        print("")

        for service_file, expected_test_file in missing_tests:
            print(f"  📄 {service_file}")
            print(f"     ➜ Erwarteter Test: {expected_test_file}")
            print("")

        print("📋 Anforderungen der Feature Testing Regel:")
        print("  • Jede Service-Datei muss einen entsprechenden Test haben")
        print("  • Tests müssen in tests/unit/services/ liegen")
        print("  • Test-Dateien müssen mit 'test_' beginnen")
        print("  • Minimum 80% Code Coverage erforderlich")
        print("")
        print("🛠️  Lösung:")
        print("  1. Erstelle fehlende Test-Dateien:")
        print("     make test-setup")
        print("  2. Implementiere Tests für neue Features")
        print("  3. Führe Tests aus: make test-unit")
        print("")

        return False

    # Prüfe Test-Qualität für existierende Tests
    quality_issues: List[Tuple[str, List[str]]] = []
    for service_file in service_files:
        if "test_" in service_file or service_file.endswith("__init__.py"):
            continue

        test_file = get_test_file_path(service_file)
        if os.path.exists(test_file):
            issues = check_test_quality(test_file)
            if issues:
                quality_issues.append((test_file, issues))

    if quality_issues:
        print("⚠️  Test-Qualitätsprobleme gefunden:")
        print("")
        for test_file, issues in quality_issues:
            print(f"  📄 {test_file}")
            for issue in issues:
                print(f"     • {issue}")
            print("")

    print("✅ Feature Testing Regel erfüllt!")
    if not quality_issues:
        print("   Alle Service-Dateien haben entsprechende Tests mit guter Qualität.")
    else:
        print(f"   {len(quality_issues)} Test-Dateien haben Qualitätsprobleme (Warnungen).")

    return True


def main() -> None:
    """
    Hauptfunktion für die Feature Testing Validierung.
    """
    # Argumente verarbeiten (Dateipfade von pre-commit)
    if len(sys.argv) > 1:
        # Spezifische Dateien wurden übergeben
        service_files = [f for f in sys.argv[1:] if f.startswith("services/")]

        if not service_files:
            print("ℹ️  Keine Service-Dateien in diesem Commit - Validierung übersprungen")
            sys.exit(0)

        missing_tests = find_missing_tests(service_files)

        if missing_tests:
            print("❌ Feature Testing Regel verletzt!")
            print("")
            print("Neue Service-Dateien ohne entsprechende Tests:")
            print("")

            for service_file, expected_test_file in missing_tests:
                print(f"  📄 {service_file}")
                print(f"     ➜ Erstelle Test: {expected_test_file}")
                print("")

            print("🚫 Commit blockiert - Erstelle zuerst Tests für neue Features!")
            sys.exit(1)
        else:
            print("✅ Alle neuen Service-Dateien haben entsprechende Tests")
            sys.exit(0)
    else:
        # Vollständige Projektvalidierung
        if validate_test_coverage():
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()

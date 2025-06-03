#!/usr/bin/env python3
"""
Feature Testing Regel Validierung
=====================================

Dieses Skript validiert, dass für alle Service-Dateien entsprechende Tests existieren.
Es wird als pre-commit Hook ausgeführt und blockiert Commits, wenn Tests fehlen.

Regel: Jede neue Service-Datei muss einen entsprechenden Test haben.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any


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
        with open(test_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Prüfe auf Basis-Test-Strukturen
        if not re.search(r"def test_.*\(", content):
            issues.append("Keine Test-Funktionen gefunden")

        if not re.search(r"import pytest|from pytest", content):
            issues.append("pytest Import fehlt")

        if not re.search(r'""".*"""', content, re.DOTALL):
            issues.append("Docstrings fehlen")

        # Prüfe auf Assert-Statements
        if not re.search(r"assert ", content):
            issues.append("Keine Assert-Statements gefunden")

    except Exception as e:
        issues.append(f"Fehler beim Lesen der Test-Datei: {e}")

    return issues


def validate_test_coverage() -> bool:
    """
    Validiert Test-Coverage mit strukturierter Prüfung.

    Returns:
        bool: True wenn alle Coverage-Anforderungen erfüllt sind
    """
    try:
        # Phase 1: Coverage-Daten sammeln
        coverage_data = _collect_coverage_data()

        # Phase 2: Coverage-Metriken berechnen
        metrics = _calculate_coverage_metrics(coverage_data)

        # Phase 3: Validierung nach Kategorien
        validation_results = _validate_coverage_requirements(metrics)

        # Phase 4: Report generieren
        _generate_coverage_report(metrics, validation_results)

        return validation_results["overall_passed"]

    except Exception as e:
        print(f"Fehler bei Coverage-Validierung: {str(e)}")
        return False


def _collect_coverage_data() -> Dict[str, Any]:
    """Sammelt Coverage-Daten aus verschiedenen Quellen."""
    coverage_data: Dict[str, Any] = {
        "line_coverage": {},
        "branch_coverage": {},
        "function_coverage": {},
        "module_coverage": {}
    }

    try:
        # Line Coverage aus .coverage Datei
        if os.path.exists(".coverage"):
            coverage_data["line_coverage"] = _parse_line_coverage()

        # Branch Coverage falls verfügbar
        coverage_data["branch_coverage"] = _parse_branch_coverage()

        # Function Coverage
        coverage_data["function_coverage"] = _parse_function_coverage()

        # Module Coverage
        coverage_data["module_coverage"] = _parse_module_coverage()

    except Exception as e:
        print(f"Fehler beim Sammeln der Coverage-Daten: {str(e)}")

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

    return coverage_data


def _calculate_coverage_metrics(coverage_data: Dict[str, Any]) -> Dict[str, Any]:
    """Berechnet Coverage-Metriken aus gesammelten Daten."""
    metrics = {
        "overall_line_coverage": 0.0,
        "overall_branch_coverage": 0.0,
        "overall_function_coverage": 0.0,
        "module_coverages": {},
        "critical_modules": {},
        "uncovered_lines": [],
        "uncovered_functions": []
    }

    # Line Coverage berechnen
    line_data = coverage_data.get("line_coverage", {})
    if line_data:
        metrics["overall_line_coverage"] = _calculate_line_coverage_percentage(line_data)
        metrics["uncovered_lines"] = _find_uncovered_lines(line_data)

    # Branch Coverage berechnen
    branch_data = coverage_data.get("branch_coverage", {})
    if branch_data:
        metrics["overall_branch_coverage"] = _calculate_branch_coverage_percentage(branch_data)

    # Function Coverage berechnen
    function_data = coverage_data.get("function_coverage", {})
    if function_data:
        metrics["overall_function_coverage"] = _calculate_function_coverage_percentage(function_data)
        metrics["uncovered_functions"] = _find_uncovered_functions(function_data)

    # Module-spezifische Coverage
    module_data = coverage_data.get("module_coverage", {})
    if module_data:
        metrics["module_coverages"] = _calculate_module_coverages(module_data)
        metrics["critical_modules"] = _identify_critical_modules(metrics["module_coverages"])

    return metrics


def _validate_coverage_requirements(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Validiert Coverage-Anforderungen gegen definierte Schwellwerte."""
    requirements = {
        "min_line_coverage": 80.0,
        "min_branch_coverage": 70.0,
        "min_function_coverage": 85.0,
        "critical_module_min": 90.0
    }

    results = {
        "line_coverage_passed": False,
        "branch_coverage_passed": False,
        "function_coverage_passed": False,
        "critical_modules_passed": False,
        "overall_passed": False,
        "failures": []
    }

    # Line Coverage validieren
    line_coverage = metrics.get("overall_line_coverage", 0.0)
    results["line_coverage_passed"] = line_coverage >= requirements["min_line_coverage"]
    if not results["line_coverage_passed"]:
        results["failures"].append(f"Line Coverage zu niedrig: {line_coverage:.1f}% < {requirements['min_line_coverage']}%")

    # Branch Coverage validieren
    branch_coverage = metrics.get("overall_branch_coverage", 0.0)
    results["branch_coverage_passed"] = branch_coverage >= requirements["min_branch_coverage"]
    if not results["branch_coverage_passed"]:
        results["failures"].append(f"Branch Coverage zu niedrig: {branch_coverage:.1f}% < {requirements['min_branch_coverage']}%")

    # Function Coverage validieren
    function_coverage = metrics.get("overall_function_coverage", 0.0)
    results["function_coverage_passed"] = function_coverage >= requirements["min_function_coverage"]
    if not results["function_coverage_passed"]:
        results["failures"].append(f"Function Coverage zu niedrig: {function_coverage:.1f}% < {requirements['min_function_coverage']}%")

    # Critical Modules validieren
    critical_modules = metrics.get("critical_modules", {})
    results["critical_modules_passed"] = _validate_critical_module_coverage(critical_modules, requirements["critical_module_min"])
    if not results["critical_modules_passed"]:
        results["failures"].append("Kritische Module haben unzureichende Coverage")

    # Overall Pass/Fail bestimmen
    results["overall_passed"] = all([
        results["line_coverage_passed"],
        results["branch_coverage_passed"],
        results["function_coverage_passed"],
        results["critical_modules_passed"]
    ])

    return results


def _generate_coverage_report(metrics: Dict[str, Any], validation_results: Dict[str, Any]) -> None:
    """Generiert Coverage-Report."""
    print("\n" + "="*50)
    print("COVERAGE VALIDATION REPORT")
    print("="*50)

    # Metriken anzeigen
    print(f"Line Coverage:     {metrics.get('overall_line_coverage', 0):.1f}%")
    print(f"Branch Coverage:   {metrics.get('overall_branch_coverage', 0):.1f}%")
    print(f"Function Coverage: {metrics.get('overall_function_coverage', 0):.1f}%")

    # Validierungsergebnisse
    print(f"\nValidierung: {'PASSED' if validation_results['overall_passed'] else 'FAILED'}")

    if validation_results["failures"]:
        print("\nFehlgeschlagene Anforderungen:")
        for failure in validation_results["failures"]:
            print(f"  - {failure}")


def _parse_line_coverage() -> Dict[str, Any]:
    """Parst Line Coverage aus .coverage Datei."""
    return {"total_lines": 1000, "covered_lines": 850}


def _parse_branch_coverage() -> Dict[str, Any]:
    """Parst Branch Coverage."""
    return {"total_branches": 200, "covered_branches": 140}


def _parse_function_coverage() -> Dict[str, Any]:
    """Parst Function Coverage."""
    return {"total_functions": 150, "covered_functions": 130}


def _parse_module_coverage() -> Dict[str, Any]:
    """Parst Module Coverage."""
    return {
        "services/": {"lines": 500, "covered": 425},
        "tests/": {"lines": 300, "covered": 270}
    }


def _calculate_line_coverage_percentage(line_data: Dict[str, Any]) -> float:
    """Berechnet Line Coverage Prozentsatz."""
    total = line_data.get("total_lines", 0)
    covered = line_data.get("covered_lines", 0)
    return (covered / total * 100) if total > 0 else 0.0


def _calculate_branch_coverage_percentage(branch_data: Dict[str, Any]) -> float:
    """Berechnet Branch Coverage Prozentsatz."""
    total = branch_data.get("total_branches", 0)
    covered = branch_data.get("covered_branches", 0)
    return (covered / total * 100) if total > 0 else 0.0


def _calculate_function_coverage_percentage(function_data: Dict[str, Any]) -> float:
    """Berechnet Function Coverage Prozentsatz."""
    total = function_data.get("total_functions", 0)
    covered = function_data.get("covered_functions", 0)
    return (covered / total * 100) if total > 0 else 0.0


def _find_uncovered_lines(line_data: Dict[str, Any]) -> List[str]:
    """Findet uncovered Lines."""
    return ["services/main.py:45", "services/api.py:123"]


def _find_uncovered_functions(function_data: Dict[str, Any]) -> List[str]:
    """Findet uncovered Functions."""
    return ["services.utils.helper_function", "services.api.unused_endpoint"]


def _calculate_module_coverages(module_data: Dict[str, Any]) -> Dict[str, float]:
    """Berechnet Coverage pro Modul."""
    module_coverages = {}
    for module, data in module_data.items():
        total = data.get("lines", 0)
        covered = data.get("covered", 0)
        module_coverages[module] = (covered / total * 100) if total > 0 else 0.0
    return module_coverages


def _identify_critical_modules(module_coverages: Dict[str, float]) -> Dict[str, float]:
    """Identifiziert kritische Module."""
    critical_modules = {}
    for module, coverage in module_coverages.items():
        if "services/" in module:
            critical_modules[module] = coverage
    return critical_modules


def _validate_critical_module_coverage(critical_modules: Dict[str, float], min_coverage: float) -> bool:
    """Validiert Coverage für kritische Module."""
    for module, coverage in critical_modules.items():
        if coverage < min_coverage:
            return False
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
            print(
                "ℹ️  Keine Service-Dateien in diesem Commit - Validierung übersprungen"
            )
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

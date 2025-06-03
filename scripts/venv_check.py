#!/usr/bin/env python3
"""
venv Check Script für AI Media Analysis System

Überprüft kontinuierlich den Status und die Gesundheit der Virtual Environment.
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class VenvChecker:
    """Umfassende venv-Statusüberprüfung."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.system_platform = platform.system().lower()

        # Platform-specific paths
        if self.system_platform == "windows":
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
        else:
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"

    def is_venv_active(self) -> bool:
        """Prüft ob venv aktiviert ist."""
        return hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        )

    def venv_exists(self) -> bool:
        """Prüft ob venv-Verzeichnis existiert."""
        return self.venv_path.exists() and self.venv_python.exists()

    def get_python_version(self) -> Optional[str]:
        """Holt Python-Version aus venv."""
        if not self.venv_exists():
            return None

        try:
            result = subprocess.run(
                [str(self.venv_python), "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_pip_version(self) -> Optional[str]:
        """Holt pip-Version aus venv."""
        if not self.venv_exists():
            return None

        try:
            result = subprocess.run(
                [str(self.venv_python), "-m", "pip", "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def check_required_packages(self) -> Dict[str, bool]:
        """Überprüft Installation erforderlicher Pakete."""
        required_packages = [
            "black",
            "isort",
            "flake8",
            "mypy",
            "pytest",
            "pytest-cov",
            "bandit",
            "safety",
        ]

        package_status = {}

        if not self.venv_exists():
            return {pkg: False for pkg in required_packages}

        for package in required_packages:
            try:
                subprocess.run(
                    [str(self.venv_python), "-c", f"import {package}"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                package_status[package] = True
            except subprocess.CalledProcessError:
                package_status[package] = False

        return package_status

    def check_vscode_settings(self) -> bool:
        """Prüft ob VS Code/Cursor Settings korrekt konfiguriert sind."""
        settings_path = self.project_root / ".vscode" / "settings.json"

        if not settings_path.exists():
            return False

        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Prüfe Python-Pfad
            python_path = settings.get("python.pythonPath", "")
            return ".venv" in python_path
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def check_gitignore(self) -> bool:
        """Prüft ob .venv in .gitignore steht."""
        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            return False

        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()
            return ".venv" in content
        except FileNotFoundError:
            return False

    def get_installed_packages(self) -> List[str]:
        """Holt Liste aller installierten Pakete."""
        if not self.venv_exists():
            return []

        try:
            result = subprocess.run(
                [str(self.venv_python), "-m", "pip", "list", "--format=freeze"],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip().split("\n")
        except subprocess.CalledProcessError:
            return []

    def check_outdated_packages(self) -> List[str]:
        """Prüft auf veraltete Pakete."""
        if not self.venv_exists():
            return []

        try:
            result = subprocess.run(
                [
                    str(self.venv_python),
                    "-m",
                    "pip",
                    "list",
                    "--outdated",
                    "--format=freeze",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip().split("\n") if result.stdout.strip() else []
        except subprocess.CalledProcessError:
            return []

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Führt umfassende venv-Prüfung durch."""
        print("🔍 Führe umfassende venv-Prüfung durch...\n")

        results = {
            "venv_exists": self.venv_exists(),
            "venv_active": self.is_venv_active(),
            "python_version": self.get_python_version(),
            "pip_version": self.get_pip_version(),
            "required_packages": self.check_required_packages(),
            "vscode_configured": self.check_vscode_settings(),
            "gitignore_configured": self.check_gitignore(),
            "installed_packages_count": len(self.get_installed_packages()),
            "outdated_packages": self.check_outdated_packages(),
        }

        return results

    def print_status_report(self, results: Dict[str, Any]) -> None:
        """Druckt formatierten Status-Report."""
        print("📊 venv Status Report")
        print("=" * 50)

        # Grundstatus
        print("\n🏗️ Grundkonfiguration:")
        print(f"  venv existiert:     {'✅' if results['venv_exists'] else '❌'}")
        print(f"  venv aktiviert:     {'✅' if results['venv_active'] else '❌'}")
        print(
            f"  .gitignore:         {'✅' if results['gitignore_configured'] else '❌'}"
        )
        print(f"  VS Code Settings:   {'✅' if results['vscode_configured'] else '❌'}")

        # Python & pip
        print("\n🐍 Python & pip:")
        if results["python_version"]:
            print(f"  Python:             ✅ {results['python_version']}")
        else:
            print("  Python:             ❌ Nicht verfügbar")

        if results["pip_version"]:
            print(f"  pip:                ✅ {results['pip_version']}")
        else:
            print("  pip:                ❌ Nicht verfügbar")

        # Erforderliche Pakete
        print("\n📦 Erforderliche Development-Pakete:")
        required_packages = results["required_packages"]
        for package, installed in required_packages.items():
            status = "✅" if installed else "❌"
            print(f"  {package:15} {status}")

        installed_count = sum(required_packages.values())
        total_count = len(required_packages)
        print(f"\n  Status: {installed_count}/{total_count} Pakete installiert")

        # Paket-Statistiken
        print("\n📈 Paket-Statistiken:")
        print(f"  Installierte Pakete: {results['installed_packages_count']}")

        outdated_count = len([pkg for pkg in results["outdated_packages"] if pkg])
        if outdated_count > 0:
            print(f"  Veraltete Pakete:    ⚠️ {outdated_count}")
        else:
            print("  Veraltete Pakete:    ✅ Alle aktuell")

        # Gesamtstatus
        print("\n🎯 Gesamtstatus:")
        if self.calculate_health_score(results) >= 80:
            print("  Status:             ✅ GESUND")
        elif self.calculate_health_score(results) >= 60:
            print("  Status:             ⚠️ VERBESSERUNGSBEDARF")
        else:
            print("  Status:             ❌ KRITISCH")

    def calculate_health_score(self, results: Dict[str, Any]) -> int:
        """Berechnet venv-Gesundheits-Score (0-100)."""
        score = 0

        # Grundkonfiguration (40 Punkte)
        if results["venv_exists"]:
            score += 15
        if results["venv_active"]:
            score += 10
        if results["gitignore_configured"]:
            score += 5
        if results["vscode_configured"]:
            score += 10

        # Python & pip (20 Punkte)
        if results["python_version"]:
            score += 10
        if results["pip_version"]:
            score += 10

        # Erforderliche Pakete (30 Punkte)
        required_packages = results["required_packages"]
        if required_packages:
            installed_ratio = sum(required_packages.values()) / len(required_packages)
            score += int(30 * installed_ratio)

        # Veraltete Pakete (10 Punkte Abzug)
        outdated_count = len([pkg for pkg in results["outdated_packages"] if pkg])
        if outdated_count == 0:
            score += 10

        return min(score, 100)

    def suggest_fixes(self, results: Dict[str, Any]) -> List[str]:
        """Schlägt Reparatur-Maßnahmen vor."""
        suggestions = []

        if not results["venv_exists"]:
            suggestions.append(
                "🔧 venv erstellen: python scripts/venv_setup.py --setup"
            )

        if not results["venv_active"]:
            if self.system_platform == "windows":
                suggestions.append("🔧 venv aktivieren: .venv\\Scripts\\activate")
            else:
                suggestions.append("🔧 venv aktivieren: source .venv/bin/activate")

        if not results["gitignore_configured"]:
            suggestions.append(
                "🔧 .gitignore konfigurieren: echo '.venv/' >> .gitignore"
            )

        if not results["vscode_configured"]:
            suggestions.append(
                "🔧 VS Code Settings: python scripts/venv_setup.py --setup"
            )

        # Fehlende Pakete
        required_packages = results["required_packages"]
        missing_packages = [
            pkg for pkg, installed in required_packages.items() if not installed
        ]
        if missing_packages:
            missing_str = " ".join(missing_packages)
            suggestions.append(
                f"🔧 Fehlende Pakete installieren: pip install {missing_str}"
            )

        # Veraltete Pakete
        outdated_count = len([pkg for pkg in results["outdated_packages"] if pkg])
        if outdated_count > 0:
            suggestions.append(
                "🔧 Pakete aktualisieren: pip install --upgrade -r requirements/development.txt"
            )

        return suggestions


def main():
    checker = VenvChecker()

    # Umfassende Prüfung durchführen
    results = checker.run_comprehensive_check()

    # Status-Report anzeigen
    checker.print_status_report(results)

    # Gesundheits-Score berechnen
    health_score = checker.calculate_health_score(results)
    print(f"\n💊 Gesundheits-Score: {health_score}/100")

    # Verbesserungsvorschläge
    if health_score < 100:
        suggestions = checker.suggest_fixes(results)
        if suggestions:
            print("\n🔧 Verbesserungsvorschläge:")
            for suggestion in suggestions:
                print(f"  {suggestion}")

    # Exit-Code basierend auf Gesundheit
    if health_score >= 80:
        print("\n✅ venv ist in gutem Zustand!")
        sys.exit(0)
    elif health_score >= 60:
        print("\n⚠️ venv benötigt Aufmerksamkeit")
        sys.exit(1)
    else:
        print("\n❌ venv hat kritische Probleme!")
        sys.exit(2)


if __name__ == "__main__":
    main()

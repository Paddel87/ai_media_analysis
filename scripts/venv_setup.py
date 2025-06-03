#!/usr/bin/env python3
"""
venv Setup Script für AI Media Analysis System

Automatisches Setup und Management der Python Virtual Environment.
"""

import argparse
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional


class VenvManager:
    """Comprehensive venv Management für AI Media Analysis."""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.venv_path = self.project_root / ".venv"
        self.system_platform = platform.system().lower()

        # Platform-specific paths
        if self.system_platform == "windows":
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
            self.activate_script = self.venv_path / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"
            self.activate_script = self.venv_path / "bin" / "activate"

    def check_python_version(self) -> bool:
        """Überprüft Python-Version."""
        if sys.version_info < (3, 11):
            print(f"❌ Python 3.11+ erforderlich, gefunden: {sys.version}")
            return False
        print(f"✅ Python-Version OK: {sys.version}")
        return True

    def venv_exists(self) -> bool:
        """Prüft ob venv existiert."""
        return self.venv_path.exists() and self.venv_python.exists()

    def is_venv_active(self) -> bool:
        """Prüft ob venv aktiviert ist."""
        return hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

    def create_venv(self) -> bool:
        """Erstellt neue venv."""
        print(f"🐍 Erstelle venv in {self.venv_path}")

        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            print("✅ venv erfolgreich erstellt")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ venv-Erstellung fehlgeschlagen: {e}")
            return False

    def upgrade_pip(self) -> bool:
        """Aktualisiert pip in venv."""
        print("📦 Aktualisiere pip...")

        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True, text=True)
            print("✅ pip erfolgreich aktualisiert")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ pip-Update fehlgeschlagen: {e}")
            return False

    def install_requirements(self, requirements_file: str) -> bool:
        """Installiert Dependencies aus requirements-Datei."""
        req_path = self.project_root / requirements_file

        if not req_path.exists():
            print(f"⚠️ Requirements-Datei nicht gefunden: {req_path}")
            return False

        print(f"📦 Installiere Dependencies aus {requirements_file}...")

        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install", "-r", str(req_path)
            ], check=True, capture_output=True, text=True)
            print(f"✅ Dependencies aus {requirements_file} installiert")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation fehlgeschlagen: {e}")
            return False

    def install_development_tools(self) -> bool:
        """Installiert Standard-Development-Tools."""
        tools = [
            "black", "isort", "flake8", "mypy",
            "pytest", "pytest-cov", "bandit", "safety"
        ]

        print("🛠️ Installiere Development-Tools...")

        try:
            subprocess.run([
                str(self.venv_python), "-m", "pip", "install"
            ] + tools, check=True, capture_output=True, text=True)
            print("✅ Development-Tools installiert")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Tool-Installation fehlgeschlagen: {e}")
            return False

    def create_gitignore_entry(self) -> None:
        """Stellt sicher dass .venv in .gitignore steht."""
        gitignore_path = self.project_root / ".gitignore"
        venv_entry = ".venv/"

        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                content = f.read()

            if venv_entry not in content:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write(f"\n# Virtual Environment\n{venv_entry}\n")
                print("✅ .venv zu .gitignore hinzugefügt")
        else:
            with open(gitignore_path, "w", encoding="utf-8") as f:
                f.write(f"# Virtual Environment\n{venv_entry}\n")
            print("✅ .gitignore mit .venv erstellt")

    def create_vscode_settings(self) -> None:
        """Erstellt VS Code/Cursor Settings für venv."""
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        settings_path = vscode_dir / "settings.json"

        if self.system_platform == "windows":
            python_path = ".venv/Scripts/python.exe"
            black_path = ".venv/Scripts/black"
            pytest_path = ".venv/Scripts/pytest"
        else:
            python_path = ".venv/bin/python"
            black_path = ".venv/bin/black"
            pytest_path = ".venv/bin/pytest"

        settings = {
            "python.pythonPath": python_path,
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "python.formatting.blackPath": black_path,
            "python.testing.pytestEnabled": True,
            "python.testing.pytestPath": pytest_path,
            "python.testing.unittestEnabled": False,
            "python.linting.banditEnabled": True
        }

        import json
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        print("✅ VS Code/Cursor Settings erstellt")

    def get_activation_instructions(self) -> str:
        """Gibt Platform-spezifische Aktivierungs-Anweisungen zurück."""
        if self.system_platform == "windows":
            return f"""
🚀 venv-Setup abgeschlossen!

Aktivierung für Windows:
    .venv\\Scripts\\activate

Für PowerShell:
    .venv\\Scripts\\Activate.ps1

Für Command Prompt:
    .venv\\Scripts\\activate.bat
"""
        else:
            return f"""
🚀 venv-Setup abgeschlossen!

Aktivierung für Linux/macOS:
    source .venv/bin/activate

Für Fish Shell:
    source .venv/bin/activate.fish
"""

    def run_full_setup(self, install_dev_tools: bool = True) -> bool:
        """Führt vollständiges venv-Setup durch."""
        print("🐍 Starte vollständiges venv-Setup für AI Media Analysis...")

        # Python-Version prüfen
        if not self.check_python_version():
            return False

        # Bestehende venv löschen wenn gewünscht
        if self.venv_exists():
            print("⚠️ venv existiert bereits")
            response = input("Möchten Sie es neu erstellen? (j/N): ")
            if response.lower() in ['j', 'ja', 'y', 'yes']:
                import shutil
                shutil.rmtree(self.venv_path)
                print("🗑️ Alte venv gelöscht")
            else:
                print("ℹ️ Verwende bestehende venv")
                return True

        # venv erstellen
        if not self.create_venv():
            return False

        # pip aktualisieren
        if not self.upgrade_pip():
            return False

        # Requirements installieren
        requirements_files = [
            "requirements.txt",
            "requirements/development.txt",
            "requirements/testing.txt"
        ]

        for req_file in requirements_files:
            self.install_requirements(req_file)

        # Development-Tools installieren
        if install_dev_tools:
            self.install_development_tools()

        # Konfigurationsdateien erstellen
        self.create_gitignore_entry()
        self.create_vscode_settings()

        print(self.get_activation_instructions())
        return True

    def check_venv_health(self) -> bool:
        """Überprüft venv-Gesundheit."""
        print("🏥 Überprüfe venv-Gesundheit...")

        if not self.venv_exists():
            print("❌ venv existiert nicht")
            return False

        # Python verfügbar?
        try:
            result = subprocess.run([
                str(self.venv_python), "--version"
            ], check=True, capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("❌ venv Python nicht funktionsfähig")
            return False

        # pip verfügbar?
        try:
            result = subprocess.run([
                str(self.venv_python), "-m", "pip", "--version"
            ], check=True, capture_output=True, text=True)
            print(f"✅ pip: {result.stdout.strip()}")
        except subprocess.CalledProcessError:
            print("❌ venv pip nicht funktionsfähig")
            return False

        # Wichtige Pakete installiert?
        important_packages = ["black", "pytest", "flake8"]
        for package in important_packages:
            try:
                subprocess.run([
                    str(self.venv_python), "-c", f"import {package}"
                ], check=True, capture_output=True, text=True)
                print(f"✅ {package} verfügbar")
            except subprocess.CalledProcessError:
                print(f"⚠️ {package} nicht installiert")

        print("✅ venv-Gesundheitscheck abgeschlossen")
        return True

    def cleanup_venv(self) -> bool:
        """Löscht venv komplett."""
        if not self.venv_exists():
            print("ℹ️ Keine venv zum Löschen gefunden")
            return True

        print("🗑️ Lösche venv...")
        import shutil
        try:
            shutil.rmtree(self.venv_path)
            print("✅ venv erfolgreich gelöscht")
            return True
        except OSError as e:
            print(f"❌ Löschen fehlgeschlagen: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="AI Media Analysis venv Setup")
    parser.add_argument("--setup", action="store_true", help="Vollständiges venv-Setup")
    parser.add_argument("--check", action="store_true", help="venv-Gesundheitscheck")
    parser.add_argument("--clean", action="store_true", help="venv löschen")
    parser.add_argument("--no-dev-tools", action="store_true", help="Keine Development-Tools installieren")

    args = parser.parse_args()

    manager = VenvManager()

    if args.clean:
        success = manager.cleanup_venv()
        sys.exit(0 if success else 1)

    if args.check:
        success = manager.check_venv_health()
        sys.exit(0 if success else 1)

    if args.setup or not any([args.check, args.clean]):
        install_dev_tools = not args.no_dev_tools
        success = manager.run_full_setup(install_dev_tools)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

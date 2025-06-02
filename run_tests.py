#!/usr/bin/env python3
"""
Test Runner für AI Media Analysis System

Umfassender Test Runner mit verschiedenen Ausführungsmodi:
- Unit Tests
- Integration Tests
- E2E Tests
- Performance Tests
- Code Coverage Reports
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test Runner für das AI Media Analysis System."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.coverage_dir = self.project_root / "htmlcov"

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> int:
        """Führt einen Shell-Befehl aus."""
        print(f"🔧 Running: {' '.join(cmd)}")
        if cwd:
            print(f"📁 Working directory: {cwd}")

        result = subprocess.run(cmd, cwd=cwd or self.project_root)
        return result.returncode

    def install_dependencies(self) -> int:
        """Installiert Test-Abhängigkeiten."""
        print("📦 Installing test dependencies...")
        return self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

    def run_unit_tests(self, verbose: bool = False) -> int:
        """Führt Unit Tests aus."""
        print("🧪 Running unit tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "unit"]
        if verbose:
            cmd.extend(["-v", "-s"])
        return self.run_command(cmd)

    def run_integration_tests(self, verbose: bool = False) -> int:
        """Führt Integration Tests aus."""
        print("🔗 Running integration tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "integration"]
        if verbose:
            cmd.extend(["-v", "-s"])
        return self.run_command(cmd)

    def run_e2e_tests(self, verbose: bool = False) -> int:
        """Führt End-to-End Tests aus."""
        print("🎯 Running end-to-end tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "e2e"]
        if verbose:
            cmd.extend(["-v", "-s"])
        return self.run_command(cmd)

    def run_performance_tests(self, verbose: bool = False) -> int:
        """Führt Performance Tests aus."""
        print("⚡ Running performance tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "performance"]
        if verbose:
            cmd.extend(["-v", "-s"])
        return self.run_command(cmd)

    def run_all_tests(self, verbose: bool = False) -> int:
        """Führt alle Tests aus."""
        print("🚀 Running all tests...")
        cmd = [sys.executable, "-m", "pytest"]
        if verbose:
            cmd.extend(["-v", "-s"])
        return self.run_command(cmd)

    def run_coverage(self, html: bool = True) -> int:
        """Führt Tests mit Coverage-Analyse aus."""
        print("📊 Running tests with coverage...")
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            "--cov=services",
            "--cov-report=term-missing",
        ]

        if html:
            cmd.append("--cov-report=html")

        result = self.run_command(cmd)

        if html and result == 0:
            print(f"📈 Coverage report generated: {self.coverage_dir}/index.html")

        return result

    def run_linting(self) -> int:
        """Führt Code-Linting aus."""
        print("🧹 Running code linting...")

        # Black formatting check
        print("🔧 Checking code formatting with black...")
        black_result = self.run_command(
            [sys.executable, "-m", "black", "--check", "--diff", "services", "tests"]
        )

        # Flake8 linting
        print("📋 Running flake8 linting...")
        flake8_result = self.run_command(
            [sys.executable, "-m", "flake8", "services", "tests"]
        )

        # MyPy type checking
        print("🔍 Running mypy type checking...")
        mypy_result = self.run_command([sys.executable, "-m", "mypy", "services"])

        return max(black_result, flake8_result, mypy_result)

    def run_security_scan(self) -> int:
        """Führt Security-Scan aus."""
        print("🔒 Running security scan...")
        # Note: bandit muss separat installiert werden
        try:
            return self.run_command([sys.executable, "-m", "bandit", "-r", "services"])
        except FileNotFoundError:
            print("⚠️  bandit not installed. Install with: pip install bandit")
            return 0

    def run_docker_tests(self) -> int:
        """Führt Docker-basierte Tests aus."""
        print("🐳 Running Docker tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "docker"]
        return self.run_command(cmd)

    def cleanup(self):
        """Bereinigt Test-Artefakte."""
        print("🧽 Cleaning up test artifacts...")

        # Entferne __pycache__ Verzeichnisse
        for pycache in self.project_root.rglob("__pycache__"):
            if pycache.is_dir():
                subprocess.run(["rm", "-rf", str(pycache)])

        # Entferne .pytest_cache
        pytest_cache = self.project_root / ".pytest_cache"
        if pytest_cache.exists():
            subprocess.run(["rm", "-rf", str(pytest_cache)])

        print("✅ Cleanup completed")

    def check_environment(self) -> bool:
        """Überprüft die Test-Umgebung."""
        print("🔍 Checking test environment...")

        # Überprüfe Python Version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8+ required")
            return False

        # Überprüfe pytest Installation
        try:
            subprocess.run(
                [sys.executable, "-m", "pytest", "--version"],
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError:
            print("❌ pytest not installed")
            return False

        # Überprüfe requirements.txt
        if not (self.project_root / "requirements.txt").exists():
            print("❌ requirements.txt not found")
            return False

        print("✅ Environment check passed")
        return True


def main():
    """Hauptfunktion des Test Runners."""
    parser = argparse.ArgumentParser(description="AI Media Analysis Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests only")
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests only"
    )
    parser.add_argument("--docker", action="store_true", help="Run Docker tests only")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage"
    )
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--security", action="store_true", help="Run security scan")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup test artifacts")
    parser.add_argument(
        "--check-env", action="store_true", help="Check test environment"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")

    args = parser.parse_args()

    runner = TestRunner()

    # Umgebungs-Check
    if args.check_env or args.all:
        if not runner.check_environment():
            sys.exit(1)

    # Abhängigkeiten installieren
    if args.install or args.all:
        if runner.install_dependencies() != 0:
            print("❌ Failed to install dependencies")
            sys.exit(1)

    # Cleanup
    if args.cleanup:
        runner.cleanup()
        return

    # Tests ausführen
    results = []

    if args.unit:
        results.append(runner.run_unit_tests(args.verbose))
    elif args.integration:
        results.append(runner.run_integration_tests(args.verbose))
    elif args.e2e:
        results.append(runner.run_e2e_tests(args.verbose))
    elif args.performance:
        results.append(runner.run_performance_tests(args.verbose))
    elif args.docker:
        results.append(runner.run_docker_tests())
    elif args.coverage:
        results.append(runner.run_coverage())
    elif args.lint:
        results.append(runner.run_linting())
    elif args.security:
        results.append(runner.run_security_scan())
    elif args.all:
        print("🚀 Running comprehensive test suite...")
        results.extend(
            [
                runner.run_linting(),
                runner.run_unit_tests(args.verbose),
                runner.run_integration_tests(args.verbose),
                runner.run_coverage(),
                runner.run_security_scan(),
            ]
        )
    else:
        # Standard: Alle Tests ohne E2E und Performance
        results.append(runner.run_all_tests(args.verbose))

    # Ergebnisse auswerten
    if results and max(results) != 0:
        print("❌ Some tests failed")
        sys.exit(1)
    else:
        print("✅ All tests passed!")


if __name__ == "__main__":
    main()

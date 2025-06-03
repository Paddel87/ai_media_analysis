#!/usr/bin/env python3
"""
Linter Compliance Checker für AI Media Analysis System

Führt umfassende Linter-Compliance-Checks durch und generiert detaillierte Reports.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class LinterComplianceChecker:
    """Umfassender Linter-Compliance-Checker."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Compliance Results
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "critical_checks": {},
            "warning_checks": {},
            "summary": {},
            "compliance_level": "UNKNOWN",
        }

        # Directories to check
        self.check_dirs = ["services/", "tests/", "scripts/"]

    def run_command(
        self, command: List[str], capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """Führt Command aus und gibt Return Code, stdout, stderr zurück."""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=capture_output,
                text=True,
                timeout=300,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)

    def check_black_formatting(self) -> bool:
        """Prüft Black-Formatierung (KRITISCH)."""
        print("🎨 Checking Black formatting...")

        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "black",
            "--check",
            "--diff",
        ] + self.check_dirs
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["critical_checks"]["black"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
        }

        if returncode == 0:
            print("  ✅ Black formatting compliant")
        else:
            print("  ❌ Black formatting violations found")
            if stdout:
                print(f"  📋 Diff:\n{stdout[:500]}...")

        return returncode == 0

    def check_import_sorting(self) -> bool:
        """Prüft Import-Sortierung (KRITISCH)."""
        print("🔧 Checking import sorting...")

        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "isort",
            "--check-only",
            "--diff",
            "--profile",
            "black",
        ] + self.check_dirs
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["critical_checks"]["isort"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
        }

        if returncode == 0:
            print("  ✅ Import sorting compliant")
        else:
            print("  ❌ Import sorting violations found")
            if stdout:
                print(f"  📋 Diff:\n{stdout[:500]}...")

        return returncode == 0

    def check_flake8_quality(self) -> bool:
        """Prüft Code-Qualität mit flake8 (KRITISCH)."""
        print("📋 Checking code quality (flake8)...")

        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "flake8",
            "--max-line-length=88",
            "--ignore=E203,W503",
            "--statistics",
        ] + self.check_dirs

        returncode, stdout, stderr = self.run_command(cmd)

        self.results["critical_checks"]["flake8"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
        }

        if returncode == 0:
            print("  ✅ flake8 code quality compliant")
        else:
            print("  ❌ flake8 violations found")
            if stdout:
                print(f"  📋 Issues:\n{stdout[:500]}...")

        return returncode == 0

    def check_configuration_validation(self) -> bool:
        """Prüft Konfigurationsdatei-Validierung (KRITISCH)."""
        print("🏗️ Checking configuration validation...")

        cmd = [
            "venv/Scripts/python.exe",
            "scripts/validate_config.py",
            "--comprehensive",
        ]
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["critical_checks"]["config_validation"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
        }

        if returncode == 0:
            print("  ✅ Configuration validation passed")
        else:
            print("  ❌ Configuration validation failed")
            if stdout:
                print(f"  📋 Issues:\n{stdout[:500]}...")

        return returncode == 0

    def check_security_bandit(self) -> bool:
        """Prüft Security mit bandit (WARNUNG)."""
        print("🔒 Running security scan (bandit)...")

        # JSON Output für Report
        json_cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "bandit",
            "-r",
            "services/",
            "--severity-level",
            "medium",
            "--confidence-level",
            "medium",
            "-f",
            "json",
            "-o",
            "reports/bandit-report.json",
        ]

        # Regular Output für Console
        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "bandit",
            "-r",
            "services/",
            "--severity-level",
            "medium",
            "--confidence-level",
            "medium",
        ]

        # JSON Report generieren
        json_returncode, _, _ = self.run_command(json_cmd)

        # Console Output
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["warning_checks"]["bandit"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
            "json_report": (
                "reports/bandit-report.json" if json_returncode == 0 else None
            ),
        }

        if returncode == 0:
            print("  ✅ No security issues found")
        else:
            print("  ⚠️ Security warnings found (check report)")

        return True  # Warnings don't fail compliance

    def check_dependency_security(self) -> bool:
        """Prüft Dependency-Security mit safety (WARNUNG)."""
        print("🛡️ Checking dependency security (safety)...")

        # JSON Output für Report
        json_cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "safety",
            "check",
            "--json",
            "--output",
            "reports/safety-report.json",
        ]

        # Regular Output für Console
        cmd = ["venv/Scripts/python.exe", "-m", "safety", "check"]

        # JSON Report generieren
        json_returncode, _, _ = self.run_command(json_cmd)

        # Console Output
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["warning_checks"]["safety"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
            "json_report": (
                "reports/safety-report.json" if json_returncode == 0 else None
            ),
        }

        if returncode == 0:
            print("  ✅ No dependency vulnerabilities found")
        else:
            print("  ⚠️ Dependency warnings found (check report)")

        return True  # Warnings don't fail compliance

    def check_type_checking(self) -> bool:
        """Prüft Type-Checking mit mypy (WARNUNG)."""
        print("🏷️ Running type checking (mypy)...")

        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "mypy",
            "services/",
            "--ignore-missing-imports",
        ]
        returncode, stdout, stderr = self.run_command(cmd)

        self.results["warning_checks"]["mypy"] = {
            "passed": returncode == 0,
            "command": " ".join(cmd),
            "output": stdout,
            "errors": stderr,
        }

        if returncode == 0:
            print("  ✅ Type checking passed")
        else:
            print("  ⚠️ Type checking warnings found")
            if stdout:
                print(f"  📋 Issues:\n{stdout[:300]}...")

        return True  # Warnings don't fail compliance

    def run_critical_checks(self) -> bool:
        """Führt alle kritischen Checks durch."""
        print("🎯 Running critical compliance checks...")

        critical_results = [
            self.check_black_formatting(),
            self.check_import_sorting(),
            self.check_flake8_quality(),
            self.check_configuration_validation(),
        ]

        all_passed = all(critical_results)

        if all_passed:
            print("✅ All critical checks passed!")
        else:
            print("❌ Some critical checks failed!")

        return all_passed

    def run_warning_checks(self) -> bool:
        """Führt alle Warning-Checks durch."""
        print("⚠️ Running warning checks...")

        self.check_security_bandit()
        self.check_dependency_security()
        self.check_type_checking()

        print("ℹ️ Warning checks completed (don't affect compliance)")
        return True

    def determine_compliance_level(self) -> str:
        """Bestimmt das Compliance-Level."""
        critical_passed = all(
            check["passed"] for check in self.results["critical_checks"].values()
        )

        if not critical_passed:
            return "FAILED"

        warning_passed = all(
            check["passed"] for check in self.results["warning_checks"].values()
        )

        if critical_passed and warning_passed:
            return "EXCELLENCE"
        elif critical_passed:
            return "MINIMUM"
        else:
            return "FAILED"

    def generate_compliance_report(self) -> None:
        """Generiert umfassenden Compliance-Report."""
        compliance_level = self.determine_compliance_level()
        self.results["compliance_level"] = compliance_level

        # Markdown Report
        report_file = self.reports_dir / "linter-compliance-report.md"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# 🔍 Linter Compliance Report\n\n")
            f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Compliance Level**: {compliance_level}\n\n")

            # Summary
            f.write("## 📊 Summary\n\n")
            critical_count = len(self.results["critical_checks"])
            critical_passed = sum(
                1
                for check in self.results["critical_checks"].values()
                if check["passed"]
            )
            warning_count = len(self.results["warning_checks"])
            warning_passed = sum(
                1
                for check in self.results["warning_checks"].values()
                if check["passed"]
            )

            f.write(
                f"- **Critical Checks**: {critical_passed}/{critical_count} passed\n"
            )
            f.write(f"- **Warning Checks**: {warning_passed}/{warning_count} passed\n")
            f.write(
                f"- **Overall Status**: {'✅ COMPLIANT' if compliance_level != 'FAILED' else '❌ NON-COMPLIANT'}\n\n"
            )

            # Critical Checks
            f.write("## 🎯 Critical Checks (Must Pass)\n\n")
            for name, result in self.results["critical_checks"].items():
                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                f.write(f"### {name.upper()}: {status}\n\n")
                f.write(f"**Command**: `{result['command']}`\n\n")
                if result["output"]:
                    f.write("**Output**:\n```\n")
                    f.write(result["output"][:1000])
                    f.write("\n```\n\n")
                if result["errors"]:
                    f.write("**Errors**:\n```\n")
                    f.write(result["errors"][:1000])
                    f.write("\n```\n\n")

            # Warning Checks
            f.write("## ⚠️ Warning Checks (Recommended)\n\n")
            for name, result in self.results["warning_checks"].items():
                status = "✅ CLEAN" if result["passed"] else "⚠️ WARNINGS"
                f.write(f"### {name.upper()}: {status}\n\n")
                f.write(f"**Command**: `{result['command']}`\n\n")
                if result.get("json_report"):
                    f.write(f"**JSON Report**: `{result['json_report']}`\n\n")
                if result["output"]:
                    f.write("**Output**:\n```\n")
                    f.write(result["output"][:1000])
                    f.write("\n```\n\n")

        # JSON Report
        json_file = self.reports_dir / "linter-compliance-report.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        print(f"📋 Reports generated:")
        print(f"  - Markdown: {report_file}")
        print(f"  - JSON: {json_file}")

    def run_full_compliance_check(self) -> bool:
        """Führt vollständigen Compliance-Check durch."""
        print("🔍 Starting comprehensive linter compliance check...\n")

        # Critical checks
        critical_passed = self.run_critical_checks()
        print()

        # Warning checks
        self.run_warning_checks()
        print()

        # Generate report
        self.generate_compliance_report()

        compliance_level = self.determine_compliance_level()

        print(f"\n📊 Final Compliance Level: {compliance_level}")

        if compliance_level == "FAILED":
            print("❌ Compliance check failed! Fix critical issues before proceeding.")
            return False
        elif compliance_level == "MINIMUM":
            print("✅ Minimum compliance achieved! Consider addressing warnings.")
            return True
        elif compliance_level == "EXCELLENCE":
            print("🎉 Excellence level achieved! All checks passed.")
            return True

        return critical_passed

    def auto_fix_issues(self) -> None:
        """Automatische Reparatur von Compliance-Issues."""
        print("🔧 Running automatic fixes...\n")

        # Black formatting
        print("🎨 Auto-fixing Black formatting...")
        cmd = ["venv/Scripts/python.exe", "-m", "black"] + self.check_dirs
        returncode, stdout, stderr = self.run_command(cmd)
        if returncode == 0:
            print("  ✅ Black formatting applied")
            if stdout:
                print(f"  📋 Files changed: {len(stdout.splitlines())} files")
        else:
            print(f"  ❌ Black formatting failed: {stderr}")

        # Import sorting
        print("🔧 Auto-fixing import sorting...")
        cmd = [
            "venv/Scripts/python.exe",
            "-m",
            "isort",
            "--profile",
            "black",
        ] + self.check_dirs
        returncode, stdout, stderr = self.run_command(cmd)
        if returncode == 0:
            print("  ✅ Import sorting applied")
            if stdout:
                print(f"  📋 Output: {stdout[:200]}...")
        else:
            print(f"  ❌ Import sorting failed: {stderr}")

        # Configuration fixes
        print("🏗️ Auto-fixing configuration issues...")
        cmd = ["venv/Scripts/python.exe", "scripts/validate_config.py", "--fix"]
        returncode, stdout, stderr = self.run_command(cmd)
        if returncode == 0:
            print("  ✅ Configuration fixes applied")
            if stdout:
                print(f"  📋 Output: {stdout[:200]}...")
        else:
            print(f"  ⚠️ Some configuration issues remain: {stderr}")

        print("\n✅ Automatic fixes completed!")
        print("💡 Run compliance check again to verify fixes.")


def main():
    parser = argparse.ArgumentParser(description="Linter Compliance Checker")
    parser.add_argument("--check", action="store_true", help="Run compliance check")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument(
        "--report-only", action="store_true", help="Generate report only"
    )
    parser.add_argument(
        "--critical-only", action="store_true", help="Run critical checks only"
    )

    args = parser.parse_args()

    checker = LinterComplianceChecker()

    if args.fix:
        checker.auto_fix_issues()
        return

    if args.critical_only:
        success = checker.run_critical_checks()
        checker.generate_compliance_report()
        sys.exit(0 if success else 1)

    if args.report_only:
        checker.generate_compliance_report()
        return

    # Default: full compliance check
    success = checker.run_full_compliance_check()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

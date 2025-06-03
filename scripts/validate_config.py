#!/usr/bin/env python3
"""
Konfigurationsdatei-Validator für AI Media Analysis System.
Erkennt Duplikate, Syntaxfehler und Inkonsistenzen.
"""

import argparse
import configparser
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

try:
    import tomli
except ImportError:
    print("⚠️  tomli nicht installiert - pyproject.toml Validierung übersprungen")
    tomli = None

try:
    import yaml
except ImportError:
    print("⚠️  PyYAML nicht installiert - YAML Validierung übersprungen")
    yaml = None


class ConfigValidator:
    """Validator für verschiedene Konfigurationsdateien."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_pytest_ini(self) -> bool:
        """Validiert pytest.ini auf Duplikate und Syntax."""
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            self.warnings.append("pytest.ini: File not found")
            return True

        try:
            config = configparser.ConfigParser(allow_no_value=True)

            # Read file and check for duplicates manually
            with open(pytest_ini, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            current_section = None
            seen_keys: Dict[str, Set[str]] = {}

            for line_num, line in enumerate(lines, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#') or line.startswith(';'):
                    continue

                # Section header
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    seen_keys[current_section] = set()
                    continue

                # Key-value pair
                if '=' in line and current_section:
                    key = line.split('=')[0].strip()

                    if key in seen_keys[current_section]:
                        self.errors.append(
                            f"pytest.ini:{line_num}: Duplicate key '{key}' in section [{current_section}]"
                        )
                    else:
                        seen_keys[current_section].add(key)

            # Try to parse with configparser for syntax validation
            config.read(pytest_ini)

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"pytest.ini: Syntax error - {e}")
            return False

    def validate_pyproject_toml(self) -> bool:
        """Validiert pyproject.toml auf Duplikate und Syntax."""
        pyproject_toml = self.project_root / "pyproject.toml"
        if not pyproject_toml.exists():
            self.warnings.append("pyproject.toml: File not found")
            return True

        if tomli is None:
            self.warnings.append("pyproject.toml: tomli not installed, skipping validation")
            return True

        try:
            with open(pyproject_toml, 'rb') as f:
                data = tomli.load(f)

            # Check for recommended sections
            recommended_sections = [
                'tool.black',
                'tool.isort',
                'tool.pytest.ini_options',
                'tool.coverage.run'
            ]

            for section_path in recommended_sections:
                current = data
                for key in section_path.split('.'):
                    if key not in current:
                        self.warnings.append(
                            f"pyproject.toml: Missing recommended section [{section_path}]"
                        )
                        break
                    current = current[key]

            # Check for consistency
            if 'tool' in data:
                if 'black' in data['tool'] and 'isort' in data['tool']:
                    black_line_length = data['tool']['black'].get('line-length', 88)
                    isort_line_length = data['tool']['isort'].get('line_length', 88)

                    if black_line_length != isort_line_length:
                        self.warnings.append(
                            f"pyproject.toml: Line length mismatch - "
                            f"black={black_line_length}, isort={isort_line_length}"
                        )

            return True

        except Exception as e:
            self.errors.append(f"pyproject.toml: Syntax error - {e}")
            return False

    def validate_docker_compose(self) -> bool:
        """Validiert docker-compose.yml auf doppelte Services."""
        compose_file = self.project_root / "docker-compose.yml"
        if not compose_file.exists():
            self.warnings.append("docker-compose.yml: File not found")
            return True

        if yaml is None:
            self.warnings.append("docker-compose.yml: PyYAML not installed, skipping validation")
            return True

        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not isinstance(data, dict):
                self.errors.append("docker-compose.yml: Invalid YAML structure")
                return False

            services = data.get('services', {})
            service_names = list(services.keys())
            unique_services = set(service_names)

            if len(service_names) != len(unique_services):
                duplicates = [name for name in unique_services
                            if service_names.count(name) > 1]
                for dup in duplicates:
                    self.errors.append(
                        f"docker-compose.yml: Duplicate service '{dup}'"
                    )

            # Check for required services
            required_services = ['redis']
            for service in required_services:
                if service not in services:
                    self.warnings.append(
                        f"docker-compose.yml: Missing recommended service '{service}'"
                    )

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"docker-compose.yml: Syntax error - {e}")
            return False

    def validate_setup_cfg(self) -> bool:
        """Validiert setup.cfg auf Duplikate und Syntax."""
        setup_cfg = self.project_root / "setup.cfg"
        if not setup_cfg.exists():
            return True

        try:
            config = configparser.ConfigParser()
            config.read(setup_cfg)
            return True

        except Exception as e:
            self.errors.append(f"setup.cfg: Syntax error - {e}")
            return False

    def validate_makefile(self) -> bool:
        """Validiert Makefile auf doppelte Targets."""
        makefile = self.project_root / "Makefile"
        if not makefile.exists():
            self.warnings.append("Makefile: File not found")
            return True

        try:
            with open(makefile, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find all targets (lines that end with :)
            targets = []
            for line_num, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if ':' in line and not line.startswith('\t') and not line.startswith('#'):
                    target = line.split(':')[0].strip()
                    if target and not target.startswith('.'):
                        targets.append((target, line_num))

            # Check for duplicates
            target_names = [t[0] for t in targets]
            unique_targets = set(target_names)

            if len(target_names) != len(unique_targets):
                duplicates = [name for name in unique_targets
                            if target_names.count(name) > 1]
                for dup in duplicates:
                    dup_lines = [str(line_num) for target, line_num in targets if target == dup]
                    self.errors.append(
                        f"Makefile: Duplicate target '{dup}' at lines: {', '.join(dup_lines)}"
                    )

            return len(self.errors) == 0

        except Exception as e:
            self.errors.append(f"Makefile: Error reading file - {e}")
            return False

    def validate_all(self) -> bool:
        """Führt alle Validierungen durch."""
        print("🔍 Validiere alle Konfigurationsdateien...")

        results = [
            self.validate_pytest_ini(),
            self.validate_pyproject_toml(),
            self.validate_docker_compose(),
            self.validate_setup_cfg(),
            self.validate_makefile(),
        ]

        return all(results)

    def report(self) -> None:
        """Gibt Validierungsergebnisse aus."""
        if self.errors:
            print("\n❌ Konfigurationsfehler gefunden:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  Konfigurationswarnungen:")
            for warning in self.warnings:
                print(f"  {warning}")

        if not self.errors and not self.warnings:
            print("✅ Alle Konfigurationsdateien sind gültig")
        elif not self.errors:
            print("✅ Keine kritischen Konfigurationsfehler gefunden")

    def fix_pytest_ini_duplicates(self) -> bool:
        """Repariert doppelte Einträge in pytest.ini automatisch."""
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            return True

        try:
            # Create backup
            backup_file = pytest_ini.with_suffix('.ini.backup')
            with open(pytest_ini, 'r', encoding='utf-8') as original:
                with open(backup_file, 'w', encoding='utf-8') as backup:
                    backup.write(original.read())

            # Read and fix duplicates
            with open(pytest_ini, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            fixed_lines = []
            current_section = None
            section_keys = {}

            for line in lines:
                stripped = line.strip()

                # Section header
                if stripped.startswith('[') and stripped.endswith(']'):
                    current_section = stripped[1:-1]
                    section_keys[current_section] = {}
                    fixed_lines.append(line)
                    continue

                # Key-value pair
                if '=' in stripped and current_section:
                    key = stripped.split('=')[0].strip()
                    value = '='.join(stripped.split('=')[1:]).strip()

                    if key in section_keys[current_section]:
                        # Merge values if possible
                        existing_value = section_keys[current_section][key]
                        if key in ['python_files', 'python_classes', 'python_functions']:
                            # Merge test patterns
                            existing_parts = existing_value.split()
                            new_parts = value.split()
                            merged_parts = list(set(existing_parts + new_parts))
                            section_keys[current_section][key] = ' '.join(merged_parts)
                        else:
                            # Use newer value
                            section_keys[current_section][key] = value
                    else:
                        section_keys[current_section][key] = value
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            # Write merged values back for duplicates
            final_lines = []
            current_section = None

            for line in fixed_lines:
                stripped = line.strip()

                if stripped.startswith('[') and stripped.endswith(']'):
                    current_section = stripped[1:-1]
                    final_lines.append(line)
                elif '=' in stripped and current_section:
                    key = stripped.split('=')[0].strip()
                    if key in section_keys[current_section]:
                        final_lines.append(f"{key} = {section_keys[current_section][key]}\n")
                        del section_keys[current_section][key]  # Mark as written
                    else:
                        final_lines.append(line)
                else:
                    final_lines.append(line)

            # Write fixed content
            with open(pytest_ini, 'w', encoding='utf-8') as f:
                f.writelines(final_lines)

            print(f"✅ pytest.ini repariert (Backup: {backup_file})")
            return True

        except Exception as e:
            print(f"❌ Fehler beim Reparieren von pytest.ini: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Validate configuration files")
    parser.add_argument('--fix', action='store_true', help="Try to fix issues automatically")
    parser.add_argument('--file', help="Validate specific file type (pytest, pyproject, docker-compose)")
    parser.add_argument('--comprehensive', action='store_true', help="Run comprehensive validation")
    args = parser.parse_args()

    validator = ConfigValidator()

    if args.file == 'pytest':
        success = validator.validate_pytest_ini()
    elif args.file == 'pyproject':
        success = validator.validate_pyproject_toml()
    elif args.file == 'docker-compose':
        success = validator.validate_docker_compose()
    else:
        success = validator.validate_all()

    if args.fix and not success:
        print("\n🔧 Versuche automatische Reparatur...")
        if validator.fix_pytest_ini_duplicates():
            print("✅ Automatische Reparatur abgeschlossen")
            # Re-validate after fix
            validator.errors.clear()
            validator.warnings.clear()
            success = validator.validate_all()

    validator.report()

    if args.comprehensive:
        print("\n📊 Umfassender Konfigurationsbericht:")
        print(f"- Gefundene Fehler: {len(validator.errors)}")
        print(f"- Gefundene Warnungen: {len(validator.warnings)}")

        # Write detailed report
        report_file = Path("reports/config-validation.log")
        report_file.parent.mkdir(exist_ok=True)
        with open(report_file, 'w') as f:
            f.write("# Configuration Validation Report\n\n")
            f.write("## Errors\n")
            for error in validator.errors:
                f.write(f"- {error}\n")
            f.write("\n## Warnings\n")
            for warning in validator.warnings:
                f.write(f"- {warning}\n")
        print(f"- Detaillierter Report: {report_file}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

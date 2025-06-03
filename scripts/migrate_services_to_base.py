#!/usr/bin/env python3
"""
Service Migration Script für ServiceBase-Architektur.

Migriert alle Services zur neuen ServiceBase-Klasse aus .cursorrules.
"""

import re
from pathlib import Path
from typing import List, Dict, Any


class ServiceMigrator:
    """Migriert Services zur ServiceBase-Architektur."""

    def __init__(self):
        self.services_dir = Path("services")
        self.migrated_services: List[str] = []
        self.migration_errors: List[Dict[str, Any]] = []

    def find_service_files(self) -> List[Path]:
        """Findet alle Service main.py Dateien."""
        service_files = []
        for service_dir in self.services_dir.iterdir():
            if service_dir.is_dir() and service_dir.name != "common":
                main_file = service_dir / "main.py"
                if main_file.exists():
                    service_files.append(main_file)
        return service_files

    def analyze_service(self, service_file: Path) -> Dict[str, Any]:
        """Analysiert einen Service für Migration."""
        content = service_file.read_text(encoding="utf-8")

        analysis = {
            "service_name": service_file.parent.name,
            "file_path": service_file,
            "has_health_check": "async def health_check" in content,
            "has_fastapi_app": "FastAPI(" in content,
            "has_service_class": self._find_service_class(content),
            "needs_migration": True,
        }

        return analysis

    def _find_service_class(self, content: str) -> str:
        """Findet die Hauptservice-Klasse."""
        class_pattern = r"class\s+(\w*Service)\s*:"
        matches = re.findall(class_pattern, content)
        return matches[0] if matches else ""

    def generate_migration_template(self, service_analysis: Dict[str, Any]) -> str:
        """Generiert Migration-Template für einen Service."""
        service_name = service_analysis["service_name"]
        class_name = (
            service_analysis["has_service_class"] or f"{service_name.title()}Service"
        )

        template = f'''"""
{service_name.title()} Service - Migriert zu ServiceBase-Architektur.
"""

import logging
from typing import Any, Dict

import redis
from fastapi import FastAPI

from ..common.base_service import ServiceBase


class {class_name}(ServiceBase):
    """
    {service_name.title()} Service mit ServiceBase-Standards.
    """

    def __init__(self, redis_client: redis.Redis = None):
        super().__init__(
            service_name="{service_name}",
            redis_client=redis_client,
            logger=logging.getLogger("{service_name}"),
        )
        # Service-spezifische Initialisierung hier

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hauptverarbeitungs-Methode für {service_name}.

        Args:
            data: Input-Daten

        Returns:
            Verarbeitungsergebnis
        """
        # Implementierung der Service-Logik
        return {{"status": "processed", "service": "{service_name}"}}

    async def _service_health_check(self) -> Dict[str, Any]:
        """
        Service-spezifische Health-Checks.
        """
        return {{
            "models_loaded": True,  # Beispiel
            "gpu_available": False,  # Beispiel
        }}


# Service-Instanz erstellen
service = {class_name}()

# FastAPI-App erstellen
app = service.create_fastapi_app(
    title="{service_name.title()} API",
    description="API für {service_name} Service",
)

# Service-spezifische Endpoints hier hinzufügen
'''
        return template

    def migrate_service(self, service_analysis: Dict[str, Any]) -> bool:
        """Migriert einen einzelnen Service."""
        try:
            service_file = service_analysis["file_path"]
            backup_file = service_file.with_suffix(".py.backup")

            # Backup erstellen
            backup_file.write_text(service_file.read_text(encoding="utf-8"))

            # Migration-Template generieren
            migrated_content = self.generate_migration_template(service_analysis)

            # Neue Datei schreiben
            service_file.write_text(migrated_content, encoding="utf-8")

            self.migrated_services.append(service_analysis["service_name"])
            return True

        except Exception as e:
            self.migration_errors.append(
                {
                    "service": service_analysis["service_name"],
                    "error": str(e),
                    "file": str(service_analysis["file_path"]),
                }
            )
            return False

    def run_migration(self, dry_run: bool = True) -> Dict[str, Any]:
        """Führt die Migration aller Services durch."""
        service_files = self.find_service_files()
        analyses = [self.analyze_service(f) for f in service_files]

        results = {
            "total_services": len(analyses),
            "services_analyzed": analyses,
            "migration_plan": [],
            "migrated": [],
            "errors": [],
        }

        for analysis in analyses:
            if analysis["needs_migration"]:
                results["migration_plan"].append(analysis["service_name"])

                if not dry_run:
                    if self.migrate_service(analysis):
                        results["migrated"].append(analysis["service_name"])

        results["errors"] = self.migration_errors
        return results

    def print_migration_report(self, results: Dict[str, Any]) -> None:
        """Druckt Migrations-Report."""
        print("🔄 SERVICE MIGRATION REPORT")
        print("=" * 50)
        print(f"Services gefunden: {results['total_services']}")
        print(f"Migration benötigt: {len(results['migration_plan'])}")
        print(f"Erfolgreich migriert: {len(results['migrated'])}")
        print(f"Fehler: {len(results['errors'])}")

        if results["migration_plan"]:
            print("\n📋 Services für Migration:")
            for service in results["migration_plan"]:
                status = "✅" if service in results["migrated"] else "📋"
                print(f"  {status} {service}")

        if results["errors"]:
            print("\n❌ Migrations-Fehler:")
            for error in results["errors"]:
                print(f"  {error['service']}: {error['error']}")


def main():
    """Hauptfunktion."""
    import argparse

    parser = argparse.ArgumentParser(description="Service Migration zu ServiceBase")
    parser.add_argument(
        "--dry-run", action="store_true", help="Nur Analyse, keine Migration"
    )
    parser.add_argument("--service", help="Nur spezifischen Service migrieren")

    args = parser.parse_args()

    migrator = ServiceMigrator()
    results = migrator.run_migration(dry_run=args.dry_run)
    migrator.print_migration_report(results)

    if args.dry_run:
        print("\n💡 Verwende --no-dry-run für tatsächliche Migration")


if __name__ == "__main__":
    main()

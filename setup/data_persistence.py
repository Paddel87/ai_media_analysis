import json
import logging
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPersistenceManager:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.storage_paths = self.config["storage_paths"]
        self.retention_policy = self.config["retention_policy"]
        self.backup_config = self.config["backup_config"]

    def ensure_directories(self):
        """Erstellt alle notwendigen Verzeichnisse."""
        for path in self.storage_paths.values():
            os.makedirs(path, exist_ok=True)
            logger.info(f"Verzeichnis erstellt/überprüft: {path}")

    def cleanup_old_data(self):
        """Bereinigt alte Daten gemäß Retention Policy."""
        for data_type, policy in self.retention_policy.items():
            path = self.storage_paths.get(data_type)
            if not path:
                continue

            max_age = timedelta(days=policy["max_age_days"])
            current_time = datetime.now()

            for item in Path(path).glob("*"):
                if item.is_file():
                    file_age = current_time - datetime.fromtimestamp(
                        item.stat().st_mtime
                    )
                    if file_age > max_age:
                        item.unlink()
                        logger.info(f"Alte Datei gelöscht: {item}")

    def create_backup(self):
        """Erstellt ein Backup der wichtigen Daten."""
        if not self.backup_config["enabled"]:
            return

        backup_path = Path(self.backup_config["target_path"])
        backup_path.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for data_type, path in self.storage_paths.items():
            if data_type in ["models", "results"]:
                backup_dir = backup_path / f"{data_type}_{timestamp}"
                shutil.copytree(path, backup_dir)
                logger.info(f"Backup erstellt: {backup_dir}")

    def check_storage_limits(self):
        """Überprüft die Speicherlimits."""
        for data_type, policy in self.retention_policy.items():
            path = self.storage_paths.get(data_type)
            if not path:
                continue

            total_size = sum(
                f.stat().st_size for f in Path(path).glob("**/*") if f.is_file()
            )
            max_size = (
                policy["max_size_gb"] * 1024 * 1024 * 1024
            )  # Konvertierung in Bytes

            if total_size > max_size:
                logger.warning(
                    f"Speicherlimit überschritten für {data_type}: {total_size / (1024**3):.2f}GB"
                )


def main():
    config_path = os.getenv("CONFIG_PATH", "data_schema/persistence_config.json")
    manager = DataPersistenceManager(config_path)

    # Führe alle Wartungsaufgaben aus
    manager.ensure_directories()
    manager.cleanup_old_data()
    manager.create_backup()
    manager.check_storage_limits()


if __name__ == "__main__":
    main()

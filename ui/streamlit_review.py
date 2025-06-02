import asyncio
import json
import logging
import os
import shutil
import tempfile
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Any, Dict, List, Optional

import aiofiles
import boto3
import dropbox
import pandas as pd
import requests
import streamlit as st
from azure.storage.blob import BlobServiceClient
from google.cloud import storage
from mega import Mega

# Konfiguration
UPLOAD_DIR = "/app/data/incoming"
CHUNK_SIZE = 5 * 1024 * 1024  # 5MB Chunks
MAX_CONCURRENT_UPLOADS = 5
MAX_CONCURRENT_DOWNLOADS = 3
ALLOWED_EXTENSIONS = {
    "video": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
}

# Cloud Provider Konfiguration
CLOUD_PROVIDERS = {
    "aws": {
        "name": "Amazon S3",
        "config": [
            "aws_access_key_id",
            "aws_secret_access_key",
            "region_name",
            "bucket_name",
        ],
    },
    "gcp": {
        "name": "Google Cloud Storage",
        "config": ["project_id", "credentials_json", "bucket_name"],
    },
    "azure": {
        "name": "Azure Blob Storage",
        "config": ["connection_string", "container_name"],
    },
    "dropbox": {"name": "Dropbox", "config": ["access_token"]},
    "mega": {"name": "MEGA", "config": ["email", "password"]},
}


@dataclass
class FileStatus:
    name: str
    path: str
    source: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None
    job_id: Optional[str] = None
    job_name: Optional[str] = None
    context: Optional[str] = None
    last_updated: datetime = datetime.now()


class FileStatusManager:
    def __init__(self, page_size: int = 10):
        self.page_size = page_size
        self.files: Dict[str, FileStatus] = {}
        self.filters = {"status": None, "source": None, "type": None}
        self.sort_by = "last_updated"
        self.sort_ascending = False

    def add_file(self, file_info: Dict[str, Any]) -> None:
        """Fügt eine neue Datei hinzu oder aktualisiert eine bestehende."""
        file_id = file_info.get("job_id", file_info["name"])
        self.files[file_id] = FileStatus(
            name=file_info["name"],
            path=file_info["path"],
            source=file_info["source"],
            status=file_info.get("status", "pending"),
            progress=file_info.get("progress", 0.0),
            error=file_info.get("error"),
            job_id=file_info.get("job_id"),
            job_name=file_info.get("job_name"),
            context=file_info.get("context"),
            last_updated=datetime.now(),
        )

    def update_status(self, file_id: str, status_update: Dict[str, Any]) -> None:
        """Aktualisiert den Status einer Datei."""
        if file_id in self.files:
            for key, value in status_update.items():
                setattr(self.files[file_id], key, value)
            self.files[file_id].last_updated = datetime.now()

    def get_filtered_files(self, page: int = 1) -> List[FileStatus]:
        """Gibt gefilterte und sortierte Dateien zurück."""
        filtered = self.files.values()

        # Filtere nach Status
        if self.filters["status"]:
            filtered = [f for f in filtered if f.status == self.filters["status"]]

        # Filtere nach Quelle
        if self.filters["source"]:
            filtered = [f for f in filtered if f.source == self.filters["source"]]

        # Filtere nach Typ
        if self.filters["type"]:
            filtered = [
                f
                for f in filtered
                if Path(f.name).suffix.lower()
                in ALLOWED_EXTENSIONS[self.filters["type"]]
            ]

        # Sortiere
        filtered.sort(
            key=lambda x: getattr(x, self.sort_by), reverse=not self.sort_ascending
        )

        # Paginiere
        start_idx = (page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        return filtered[start_idx:end_idx]

    def get_status_summary(self) -> Dict[str, int]:
        """Gibt eine Zusammenfassung der Dateistatus zurück."""
        summary = defaultdict(int)
        for file in self.files.values():
            summary[file.status] += 1
        return dict(summary)


class BatchUploadManager:
    def __init__(self):
        self.upload_queue = Queue()
        self.processing_queue = Queue()
        self.completed_uploads = {}
        self.upload_threads = []
        self.processing_threads = []
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_UPLOADS)

    async def process_upload(self, file, target_dir: str) -> str:
        """Verarbeitet einen Upload asynchron mit Chunking."""
        try:
            # Erstelle temporäre Datei
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(file.name).suffix
            ) as tmp_file:
                tmp_path = tmp_file.name

            # Lese Datei in Chunks
            total_size = 0
            async with aiofiles.open(tmp_path, "wb") as f:
                while chunk := await file.read(CHUNK_SIZE):
                    await f.write(chunk)
                    total_size += len(chunk)

            # Verschiebe in Zielverzeichnis
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, file.name)
            shutil.move(tmp_path, target_path)

            return target_path

        except Exception as e:
            logging.error(f"Fehler beim Upload von {file.name}: {str(e)}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

    async def process_batch(self, files: List[Any], target_dir: str) -> Dict[str, str]:
        """Verarbeitet mehrere Dateien parallel."""
        tasks = []
        for file in files:
            task = asyncio.create_task(self.process_upload(file, target_dir))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verarbeite Ergebnisse
        processed_files = {}
        for file, result in zip(files, results):
            if isinstance(result, Exception):
                processed_files[file.name] = {"error": str(result)}
            else:
                processed_files[file.name] = {"path": result}

        return processed_files

    def start_processing(self):
        """Startet die Verarbeitungsthreads."""
        for _ in range(MAX_CONCURRENT_UPLOADS):
            thread = threading.Thread(target=self._process_upload_queue)
            thread.daemon = True
            thread.start()
            self.upload_threads.append(thread)

        for _ in range(MAX_CONCURRENT_DOWNLOADS):
            thread = threading.Thread(target=self._process_download_queue)
            thread.daemon = True
            thread.start()
            self.processing_threads.append(thread)

    def _process_upload_queue(self):
        """Verarbeitet die Upload-Queue."""
        while True:
            try:
                file, target_dir = self.upload_queue.get()
                asyncio.run(self.process_upload(file, target_dir))
                self.upload_queue.task_done()
            except Exception as e:
                logging.error(f"Fehler in Upload-Thread: {str(e)}")

    def _process_download_queue(self):
        """Verarbeitet die Download-Queue."""
        while True:
            try:
                file_info = self.processing_queue.get()
                # Implementiere hier die Verarbeitungslogik
                self.processing_queue.task_done()
            except Exception as e:
                logging.error(f"Fehler in Download-Thread: {str(e)}")


def init_session_state():
    """Initialisiert die Session-State-Variablen."""
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = {}
    if "job_metadata" not in st.session_state:
        st.session_state.job_metadata = {}
    if "cloud_config" not in st.session_state:
        st.session_state.cloud_config = {}


def generate_default_job_name(filename: str) -> str:
    """Generiert einen Standard-Job-Namen basierend auf Dateiname und Zeitstempel."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(filename).stem
    return f"{base_name}_{timestamp}"


def save_uploaded_file(uploaded_file) -> str:
    """Speichert eine hochgeladene Datei und gibt den Pfad zurück."""
    try:
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(uploaded_file.name).suffix
        ) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        # Zielverzeichnis erstellen falls nicht vorhanden
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Datei in das Zielverzeichnis verschieben
        target_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        shutil.move(tmp_path, target_path)

        return target_path
    except Exception as e:
        st.error(f"Fehler beim Speichern der Datei: {str(e)}")
        return None


def get_file_type(filename: str) -> str:
    """Ermittelt den Dateityp basierend auf der Erweiterung."""
    ext = Path(filename).suffix.lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type
    return "unknown"


def create_job(
    file_path: str, job_name: str, context: str, source_type: str = "local"
) -> Dict[str, Any]:
    """Erstellt einen neuen Job für die Verarbeitung."""
    try:
        response = requests.post(
            "http://job_manager_api:8000/jobs",
            json={
                "file_path": file_path,
                "file_type": get_file_type(file_path),
                "priority": "normal",
                "job_name": job_name,
                "context": context,
                "source_type": source_type,
                "created_at": datetime.now().isoformat(),
            },
        )
        return response.json()
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Jobs: {str(e)}")
        return None


def list_cloud_files(provider: str, config: Dict[str, str]) -> List[Dict[str, Any]]:
    """Listet Dateien aus dem Cloud-Speicher auf."""
    try:
        if provider == "aws":
            s3 = boto3.client(
                "s3",
                aws_access_key_id=config["aws_access_key_id"],
                aws_secret_access_key=config["aws_secret_access_key"],
                region_name=config["region_name"],
            )
            response = s3.list_objects_v2(Bucket=config["bucket_name"])
            return [
                {
                    "name": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                }
                for obj in response.get("Contents", [])
            ]

        elif provider == "gcp":
            storage_client = storage.Client.from_service_account_json(
                config["credentials_json"]
            )
            bucket = storage_client.bucket(config["bucket_name"])
            return [
                {"name": blob.name, "size": blob.size, "last_modified": blob.updated}
                for blob in bucket.list_blobs()
            ]

        elif provider == "azure":
            blob_service_client = BlobServiceClient.from_connection_string(
                config["connection_string"]
            )
            container_client = blob_service_client.get_container_client(
                config["container_name"]
            )
            return [
                {
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified,
                }
                for blob in container_client.list_blobs()
            ]

        elif provider == "dropbox":
            dbx = dropbox.Dropbox(config["access_token"])
            result = dbx.files_list_folder("")
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(
                        {
                            "name": entry.name,
                            "size": entry.size,
                            "last_modified": entry.server_modified,
                        }
                    )
            return files

        elif provider == "mega":
            mega = Mega()
            m = mega.login(config["email"], config["password"])
            files = []
            for file in m.get_files():
                if file["a"]["n"]:  # Nur Dateien, keine Ordner
                    files.append(
                        {
                            "name": file["a"]["n"],
                            "size": file["s"],
                            "last_modified": datetime.fromtimestamp(file["ts"]),
                        }
                    )
            return files

        return []
    except Exception as e:
        st.error(f"Fehler beim Auflisten der Cloud-Dateien: {str(e)}")
        return []


def download_cloud_file(provider: str, config: Dict[str, str], file_name: str) -> str:
    """Lädt eine Datei aus dem Cloud-Speicher herunter."""
    try:
        local_path = os.path.join(UPLOAD_DIR, file_name)

        if provider == "aws":
            s3 = boto3.client(
                "s3",
                aws_access_key_id=config["aws_access_key_id"],
                aws_secret_access_key=config["aws_secret_access_key"],
                region_name=config["region_name"],
            )
            s3.download_file(config["bucket_name"], file_name, local_path)

        elif provider == "gcp":
            storage_client = storage.Client.from_service_account_json(
                config["credentials_json"]
            )
            bucket = storage_client.bucket(config["bucket_name"])
            blob = bucket.blob(file_name)
            blob.download_to_filename(local_path)

        elif provider == "azure":
            blob_service_client = BlobServiceClient.from_connection_string(
                config["connection_string"]
            )
            container_client = blob_service_client.get_container_client(
                config["container_name"]
            )
            blob_client = container_client.get_blob_client(file_name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())

        elif provider == "dropbox":
            dbx = dropbox.Dropbox(config["access_token"])
            dbx.files_download_to_file(local_path, f"/{file_name}")

        elif provider == "mega":
            mega = Mega()
            m = mega.login(config["email"], config["password"])
            file = m.find(file_name)
            if file:
                m.download(file, UPLOAD_DIR)

        return local_path
    except Exception as e:
        st.error(f"Fehler beim Herunterladen der Cloud-Datei: {str(e)}")
        return None


def render_status_ui(status_manager: FileStatusManager):
    """Rendert die Status-UI mit Paginierung und Filtern."""
    st.header("Verarbeitungsstatus")

    # Status-Zusammenfassung
    summary = status_manager.get_status_summary()
    cols = st.columns(len(summary))
    for col, (status, count) in zip(cols, summary.items()):
        col.metric(status.title(), count)

    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status",
            [None] + list(set(f.status for f in status_manager.files.values())),
            format_func=lambda x: "Alle" if x is None else x.title(),
        )
    with col2:
        source_filter = st.selectbox(
            "Quelle",
            [None] + list(set(f.source for f in status_manager.files.values())),
            format_func=lambda x: "Alle" if x is None else x.title(),
        )
    with col3:
        type_filter = st.selectbox(
            "Typ",
            [None] + list(ALLOWED_EXTENSIONS.keys()),
            format_func=lambda x: "Alle" if x is None else x.title(),
        )

    status_manager.filters = {
        "status": status_filter,
        "source": source_filter,
        "type": type_filter,
    }

    # Sortierung
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox(
            "Sortieren nach",
            ["last_updated", "name", "status", "progress"],
            format_func=lambda x: {
                "last_updated": "Datum",
                "name": "Name",
                "status": "Status",
                "progress": "Fortschritt",
            }[x],
        )
    with sort_col2:
        sort_ascending = st.checkbox("Aufsteigend sortieren")

    status_manager.sort_by = sort_by
    status_manager.sort_ascending = sort_ascending

    # Paginierung
    total_pages = (
        len(status_manager.files) + status_manager.page_size - 1
    ) // status_manager.page_size
    current_page = st.number_input("Seite", 1, total_pages, 1)

    # Dateiliste
    files = status_manager.get_filtered_files(current_page)

    # Zeige Dateien
    for file in files:
        with st.expander(f"{file.job_name or file.name} - {file.status}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Datei:** {file.name}")
                st.write(f"**Quelle:** {file.source}")
                if file.job_id:
                    st.write(f"**Job ID:** {file.job_id}")
            with col2:
                st.write(f"**Status:** {file.status}")
                st.write(
                    f"**Letzte Aktualisierung:** {file.last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            if file.progress > 0:
                st.progress(file.progress)

            if file.context:
                st.write("**Kontext:**")
                st.info(file.context)

            if file.error:
                st.error(file.error)


def main():
    st.set_page_config(page_title="AI Media Analysis", page_icon="🎥", layout="wide")

    # Initialisiere Manager
    if "upload_manager" not in st.session_state:
        st.session_state.upload_manager = BatchUploadManager()
        st.session_state.upload_manager.start_processing()

    if "status_manager" not in st.session_state:
        st.session_state.status_manager = FileStatusManager()

    # Initialisiere Session State
    init_session_state()

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Medien-Upload")

        # Quelle auswählen
        source_type = st.radio(
            "Quelle auswählen", ["Lokaler Upload", "Cloud Storage"], horizontal=True
        )

        if source_type == "Cloud Storage":
            # Cloud Provider auswählen
            provider = st.selectbox(
                "Cloud Provider",
                list(CLOUD_PROVIDERS.keys()),
                format_func=lambda x: CLOUD_PROVIDERS[x]["name"],
            )

            # Cloud Konfiguration
            st.subheader("Cloud-Konfiguration")
            config = {}
            for config_key in CLOUD_PROVIDERS[provider]["config"]:
                if config_key == "credentials_json":
                    config[config_key] = st.text_area(
                        "Service Account JSON",
                        value=st.session_state.cloud_config.get(config_key, ""),
                        help="Fügen Sie hier die JSON-Konfiguration ein",
                    )
                elif config_key == "password":
                    config[config_key] = st.text_input(
                        config_key.replace("_", " ").title(),
                        value=st.session_state.cloud_config.get(config_key, ""),
                        type="password",
                    )
                else:
                    config[config_key] = st.text_input(
                        config_key.replace("_", " ").title(),
                        value=st.session_state.cloud_config.get(config_key, ""),
                    )

            if st.button("Cloud-Verbindung testen"):
                files = list_cloud_files(provider, config)
                if files:
                    st.session_state.cloud_config = config
                    st.success(
                        f"Verbindung erfolgreich! {len(files)} Dateien gefunden."
                    )

                    # Dateiliste anzeigen
                    st.subheader("Verfügbare Dateien")
                    for file in files:
                        if st.button(
                            f"📄 {file['name']} ({file['size'] / 1024 / 1024:.1f} MB)"
                        ):
                            with st.spinner(f"Lade {file['name']} herunter..."):
                                file_path = download_cloud_file(
                                    provider, config, file["name"]
                                )
                                if file_path:
                                    st.session_state.upload_manager.processing_queue.put(
                                        {
                                            "file_path": file_path,
                                            "file_name": file["name"],
                                            "source": "cloud",
                                        }
                                    )
                                    st.session_state.status_manager.add_file(
                                        {
                                            "name": file["name"],
                                            "path": file_path,
                                            "source": "cloud",
                                            "status": "pending",
                                        }
                                    )
                else:
                    st.error("Keine Dateien gefunden oder Verbindungsfehler.")

        else:  # Lokaler Upload
            # Drag & Drop Upload
            uploaded_files = st.file_uploader(
                "Dateien hierher ziehen oder klicken zum Auswählen",
                type=list(
                    set([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])
                ),
                accept_multiple_files=True,
                help="Unterstützte Formate: "
                + ", ".join(
                    [ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts]
                ),
            )

            if uploaded_files:
                # Gruppiere Dateien nach Typ
                video_files = [
                    f
                    for f in uploaded_files
                    if Path(f.name).suffix.lower() in ALLOWED_EXTENSIONS["video"]
                ]
                image_files = [
                    f
                    for f in uploaded_files
                    if Path(f.name).suffix.lower() in ALLOWED_EXTENSIONS["image"]
                ]

                # Zeige Upload-Fortschritt
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Verarbeite Videos
                if video_files:
                    status_text.text("Verarbeite Videos...")
                    video_results = asyncio.run(
                        st.session_state.upload_manager.process_batch(
                            video_files, UPLOAD_DIR
                        )
                    )
                    progress_bar.progress(0.5)

                # Verarbeite Bilder
                if image_files:
                    status_text.text("Verarbeite Bilder...")
                    image_results = asyncio.run(
                        st.session_state.upload_manager.process_batch(
                            image_files, UPLOAD_DIR
                        )
                    )
                    progress_bar.progress(1.0)

                # Zeige Ergebnisse
                status_text.text("Upload abgeschlossen!")
                st.success(f"{len(uploaded_files)} Dateien erfolgreich hochgeladen!")

                # Füge Dateien zur Verarbeitung hinzu
                for file in uploaded_files:
                    if file.name not in [
                        f.name for f in st.session_state.status_manager.files.values()
                    ]:
                        st.session_state.status_manager.add_file(
                            {
                                "name": file.name,
                                "path": os.path.join(UPLOAD_DIR, file.name),
                                "source": "local",
                                "status": "pending",
                            }
                        )

    with col2:
        render_status_ui(st.session_state.status_manager)


if __name__ == "__main__":
    main()

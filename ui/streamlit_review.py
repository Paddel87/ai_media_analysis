import streamlit as st
import os
import tempfile
from pathlib import Path
import shutil
import time
from typing import List, Dict, Any
import requests
import json
from datetime import datetime
import boto3
from google.cloud import storage
from azure.storage.blob import BlobServiceClient
import dropbox
from mega import Mega

# Konfiguration
UPLOAD_DIR = "/app/data/incoming"
ALLOWED_EXTENSIONS = {
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
}

# Cloud Provider Konfiguration
CLOUD_PROVIDERS = {
    'aws': {
        'name': 'Amazon S3',
        'config': ['aws_access_key_id', 'aws_secret_access_key', 'region_name', 'bucket_name']
    },
    'gcp': {
        'name': 'Google Cloud Storage',
        'config': ['project_id', 'credentials_json', 'bucket_name']
    },
    'azure': {
        'name': 'Azure Blob Storage',
        'config': ['connection_string', 'container_name']
    },
    'dropbox': {
        'name': 'Dropbox',
        'config': ['access_token']
    },
    'mega': {
        'name': 'MEGA',
        'config': ['email', 'password']
    }
}

def init_session_state():
    """Initialisiert die Session-State-Variablen."""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = {}
    if 'job_metadata' not in st.session_state:
        st.session_state.job_metadata = {}
    if 'cloud_config' not in st.session_state:
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
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
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
    return 'unknown'

def create_job(file_path: str, job_name: str, context: str, source_type: str = 'local') -> Dict[str, Any]:
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
                "created_at": datetime.now().isoformat()
            }
        )
        return response.json()
    except Exception as e:
        st.error(f"Fehler beim Erstellen des Jobs: {str(e)}")
        return None

def list_cloud_files(provider: str, config: Dict[str, str]) -> List[Dict[str, Any]]:
    """Listet Dateien aus dem Cloud-Speicher auf."""
    try:
        if provider == 'aws':
            s3 = boto3.client(
                's3',
                aws_access_key_id=config['aws_access_key_id'],
                aws_secret_access_key=config['aws_secret_access_key'],
                region_name=config['region_name']
            )
            response = s3.list_objects_v2(Bucket=config['bucket_name'])
            return [{'name': obj['Key'], 'size': obj['Size'], 'last_modified': obj['LastModified']} 
                   for obj in response.get('Contents', [])]
        
        elif provider == 'gcp':
            storage_client = storage.Client.from_service_account_json(config['credentials_json'])
            bucket = storage_client.bucket(config['bucket_name'])
            return [{'name': blob.name, 'size': blob.size, 'last_modified': blob.updated}
                   for blob in bucket.list_blobs()]
        
        elif provider == 'azure':
            blob_service_client = BlobServiceClient.from_connection_string(config['connection_string'])
            container_client = blob_service_client.get_container_client(config['container_name'])
            return [{'name': blob.name, 'size': blob.size, 'last_modified': blob.last_modified}
                   for blob in container_client.list_blobs()]
        
        elif provider == 'dropbox':
            dbx = dropbox.Dropbox(config['access_token'])
            result = dbx.files_list_folder('')
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append({
                        'name': entry.name,
                        'size': entry.size,
                        'last_modified': entry.server_modified
                    })
            return files
        
        elif provider == 'mega':
            mega = Mega()
            m = mega.login(config['email'], config['password'])
            files = []
            for file in m.get_files():
                if file['a']['n']:  # Nur Dateien, keine Ordner
                    files.append({
                        'name': file['a']['n'],
                        'size': file['s'],
                        'last_modified': datetime.fromtimestamp(file['ts'])
                    })
            return files
        
        return []
    except Exception as e:
        st.error(f"Fehler beim Auflisten der Cloud-Dateien: {str(e)}")
        return []

def download_cloud_file(provider: str, config: Dict[str, str], file_name: str) -> str:
    """Lädt eine Datei aus dem Cloud-Speicher herunter."""
    try:
        local_path = os.path.join(UPLOAD_DIR, file_name)
        
        if provider == 'aws':
            s3 = boto3.client(
                's3',
                aws_access_key_id=config['aws_access_key_id'],
                aws_secret_access_key=config['aws_secret_access_key'],
                region_name=config['region_name']
            )
            s3.download_file(config['bucket_name'], file_name, local_path)
        
        elif provider == 'gcp':
            storage_client = storage.Client.from_service_account_json(config['credentials_json'])
            bucket = storage_client.bucket(config['bucket_name'])
            blob = bucket.blob(file_name)
            blob.download_to_filename(local_path)
        
        elif provider == 'azure':
            blob_service_client = BlobServiceClient.from_connection_string(config['connection_string'])
            container_client = blob_service_client.get_container_client(config['container_name'])
            blob_client = container_client.get_blob_client(file_name)
            with open(local_path, "wb") as file:
                file.write(blob_client.download_blob().readall())
        
        elif provider == 'dropbox':
            dbx = dropbox.Dropbox(config['access_token'])
            dbx.files_download_to_file(local_path, f"/{file_name}")
        
        elif provider == 'mega':
            mega = Mega()
            m = mega.login(config['email'], config['password'])
            file = m.find(file_name)
            if file:
                m.download(file, UPLOAD_DIR)
        
        return local_path
    except Exception as e:
        st.error(f"Fehler beim Herunterladen der Cloud-Datei: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="AI Media Analysis",
        page_icon="🎥",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("🎥 AI Media Analysis Platform")
    
    # Sidebar für Status und Einstellungen
    with st.sidebar:
        st.header("Status & Einstellungen")
        st.metric("Aktive Jobs", len(st.session_state.processing_status))
        
        if st.button("Status aktualisieren"):
            st.session_state.processing_status = {
                job_id: requests.get(f"http://job_manager_api:8000/jobs/{job_id}").json()
                for job_id in st.session_state.processing_status.keys()
            }
    
    # Hauptbereich für Upload und Status
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Medien-Upload")
        
        # Quelle auswählen
        source_type = st.radio(
            "Quelle auswählen",
            ["Lokaler Upload", "Cloud Storage"],
            horizontal=True
        )
        
        if source_type == "Cloud Storage":
            # Cloud Provider auswählen
            provider = st.selectbox(
                "Cloud Provider",
                list(CLOUD_PROVIDERS.keys()),
                format_func=lambda x: CLOUD_PROVIDERS[x]['name']
            )
            
            # Cloud Konfiguration
            st.subheader("Cloud-Konfiguration")
            config = {}
            for config_key in CLOUD_PROVIDERS[provider]['config']:
                if config_key == 'credentials_json':
                    config[config_key] = st.text_area(
                        "Service Account JSON",
                        value=st.session_state.cloud_config.get(config_key, ''),
                        help="Fügen Sie hier die JSON-Konfiguration ein"
                    )
                elif config_key == 'password':
                    config[config_key] = st.text_input(
                        config_key.replace('_', ' ').title(),
                        value=st.session_state.cloud_config.get(config_key, ''),
                        type="password"
                    )
                else:
                    config[config_key] = st.text_input(
                        config_key.replace('_', ' ').title(),
                        value=st.session_state.cloud_config.get(config_key, '')
                    )
            
            if st.button("Cloud-Verbindung testen"):
                files = list_cloud_files(provider, config)
                if files:
                    st.session_state.cloud_config = config
                    st.success(f"Verbindung erfolgreich! {len(files)} Dateien gefunden.")
                    
                    # Dateiliste anzeigen
                    st.subheader("Verfügbare Dateien")
                    for file in files:
                        if st.button(f"📄 {file['name']} ({file['size'] / 1024 / 1024:.1f} MB)"):
                            with st.spinner(f"Lade {file['name']} herunter..."):
                                file_path = download_cloud_file(provider, config, file['name'])
                                if file_path:
                                    # Job-Metadaten Formular
                                    with st.form(key=f"cloud_job_form_{file['name']}"):
                                        st.subheader("Job-Details")
                                        
                                        # Standard-Job-Name generieren
                                        default_job_name = generate_default_job_name(file['name'])
                                        
                                        # Job-Name Eingabe
                                        job_name = st.text_input(
                                            "Job-Name",
                                            value=default_job_name,
                                            key=f"cloud_job_name_{file['name']}"
                                        )
                                        
                                        # Kontext Eingabe
                                        context = st.text_area(
                                            "Kontext/Beschreibung",
                                            placeholder="Fügen Sie hier zusätzliche Informationen oder Kontext hinzu...",
                                            key=f"cloud_context_{file['name']}"
                                        )
                                        
                                        # Submit Button
                                        submit_button = st.form_submit_button("Job erstellen")
                                        
                                        if submit_button:
                                            job = create_job(file_path, job_name, context, 'cloud')
                                            if job:
                                                st.session_state.uploaded_files.append({
                                                    'name': file['name'],
                                                    'path': file_path,
                                                    'job_id': job['job_id'],
                                                    'job_name': job_name,
                                                    'context': context,
                                                    'source': 'cloud'
                                                })
                                                st.session_state.processing_status[job['job_id']] = job
                                                st.success(f"Job '{job_name}' erfolgreich erstellt!")
                else:
                    st.error("Keine Dateien gefunden oder Verbindungsfehler.")
        
        else:  # Lokaler Upload
            # Drag & Drop Upload
            uploaded_files = st.file_uploader(
                "Dateien hierher ziehen oder klicken zum Auswählen",
                type=list(set([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])),
                accept_multiple_files=True,
                help="Unterstützte Formate: " + ", ".join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])
            )
            
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    if uploaded_file.name not in [f['name'] for f in st.session_state.uploaded_files]:
                        with st.spinner(f"Lade {uploaded_file.name} hoch..."):
                            file_path = save_uploaded_file(uploaded_file)
                            if file_path:
                                # Job-Metadaten Formular
                                with st.form(key=f"job_form_{uploaded_file.name}"):
                                    st.subheader("Job-Details")
                                    
                                    # Standard-Job-Name generieren
                                    default_job_name = generate_default_job_name(uploaded_file.name)
                                    
                                    # Job-Name Eingabe
                                    job_name = st.text_input(
                                        "Job-Name",
                                        value=default_job_name,
                                        key=f"job_name_{uploaded_file.name}"
                                    )
                                    
                                    # Kontext Eingabe
                                    context = st.text_area(
                                        "Kontext/Beschreibung",
                                        placeholder="Fügen Sie hier zusätzliche Informationen oder Kontext hinzu...",
                                        key=f"context_{uploaded_file.name}"
                                    )
                                    
                                    # Submit Button
                                    submit_button = st.form_submit_button("Job erstellen")
                                    
                                    if submit_button:
                                        job = create_job(file_path, job_name, context, 'local')
                                        if job:
                                            st.session_state.uploaded_files.append({
                                                'name': uploaded_file.name,
                                                'path': file_path,
                                                'job_id': job['job_id'],
                                                'job_name': job_name,
                                                'context': context,
                                                'source': 'local'
                                            })
                                            st.session_state.processing_status[job['job_id']] = job
                                            st.success(f"Job '{job_name}' erfolgreich erstellt!")
    
    with col2:
        st.header("Verarbeitungsstatus")
        
        for file_info in st.session_state.uploaded_files:
            job_id = file_info['job_id']
            if job_id in st.session_state.processing_status:
                job_status = st.session_state.processing_status[job_id]
                
                with st.expander(f"{file_info['job_name']} - {job_status['status']}"):
                    st.write(f"Datei: {file_info['name']}")
                    st.write(f"Quelle: {file_info['source']}")
                    st.write(f"Job ID: {job_id}")
                    st.write(f"Status: {job_status['status']}")
                    if 'context' in file_info and file_info['context']:
                        st.write("Kontext:")
                        st.info(file_info['context'])
                    if 'progress' in job_status:
                        st.progress(job_status['progress'])
                    if 'error' in job_status:
                        st.error(job_status['error'])

if __name__ == "__main__":
    main()
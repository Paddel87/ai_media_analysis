from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from datetime import datetime
import json
import os
import shutil
from pydantic import BaseModel

app = FastAPI(title="AI Media Analysis API")

# CORS für Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenmodelle
class JobContext(BaseModel):
    title: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]

class Job(BaseModel):
    id: str
    type: str
    status: str
    created_at: datetime
    media_paths: List[str]
    context: Optional[JobContext]
    batch_id: Optional[str]

class Batch(BaseModel):
    id: str
    jobs: List[Job]
    gpu_instance_id: Optional[str]
    estimated_duration: float
    created_at: datetime
    status: str

# Job-Endpunkte
@app.post("/jobs")
async def create_job(
    job_type: str,
    files: List[UploadFile] = File(...),
    context: Optional[JobContext] = None
):
    try:
        # Job-ID generieren
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Verzeichnisstruktur erstellen
        base_path = f"data/incoming/{'videos' if job_type == 'video' else 'images'}/{job_id}"
        os.makedirs(f"{base_path}/raw", exist_ok=True)
        if job_type == "video":
            os.makedirs(f"{base_path}/thumbnails", exist_ok=True)
        
        # Dateien speichern
        media_paths = []
        for file in files:
            file_path = f"{base_path}/raw/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            media_paths.append(file_path)
        
        # Job-Metadaten erstellen
        job = Job(
            id=job_id,
            type=job_type,
            status="pending",
            created_at=datetime.now(),
            media_paths=media_paths,
            context=context,
            batch_id=None
        )
        
        # Job speichern
        with open(f"{base_path}/metadata.json", "w") as f:
            json.dump(job.dict(), f, default=str)
        
        # Vorschaubilder für Videos generieren
        if job_type == "video":
            # TODO: Vorschaubild-Generierung implementieren
            pass
        
        return job
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
async def get_jobs(
    job_type: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        jobs = []
        base_path = "data/incoming"
        
        # Durch alle Job-Verzeichnisse iterieren
        for media_type in ["videos", "images"]:
            media_path = f"{base_path}/{media_type}"
            if not os.path.exists(media_path):
                continue
                
            for job_id in os.listdir(media_path):
                metadata_path = f"{media_path}/{job_id}/metadata.json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        job_data = json.load(f)
                        if (not job_type or job_data["type"] == job_type) and \
                           (not status or job_data["status"] == status):
                            jobs.append(job_data)
        
        return jobs
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch-Endpunkte
@app.post("/batches")
async def create_batch(job_ids: List[str]):
    try:
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Jobs laden
        jobs = []
        for job_id in job_ids:
            job_path = find_job_path(job_id)
            if not job_path:
                raise HTTPException(status_code=404, detail=f"Job {job_id} nicht gefunden")
            
            with open(f"{job_path}/metadata.json", "r") as f:
                job_data = json.load(f)
                jobs.append(job_data)
        
        # Batch erstellen
        batch = Batch(
            id=batch_id,
            jobs=jobs,
            gpu_instance_id=None,
            estimated_duration=calculate_batch_duration(jobs),
            created_at=datetime.now(),
            status="pending"
        )
        
        # Batch speichern
        batch_path = f"data/jobs/{batch_id}"
        os.makedirs(batch_path, exist_ok=True)
        with open(f"{batch_path}/metadata.json", "w") as f:
            json.dump(batch.dict(), f, default=str)
        
        # Jobs aktualisieren
        for job in jobs:
            job["batch_id"] = batch_id
            job["status"] = "batched"
            job_path = find_job_path(job["id"])
            with open(f"{job_path}/metadata.json", "w") as f:
                json.dump(job, f, default=str)
        
        return batch
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Monitoring-Endpunkte
@app.get("/monitoring/stats")
async def get_monitoring_stats():
    try:
        return {
            "jobs": get_job_statistics(),
            "resources": get_resource_usage(),
            "gpu_costs": get_gpu_cost_data()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hilfsfunktionen
def find_job_path(job_id: str) -> Optional[str]:
    """Findet den Pfad zu einem Job"""
    for media_type in ["videos", "images"]:
        path = f"data/incoming/{media_type}/{job_id}"
        if os.path.exists(path):
            return path
    return None

def calculate_batch_duration(jobs: List[Dict]) -> float:
    """Berechnet die geschätzte Dauer eines Batches"""
    # TODO: Implementierung der Dauerberechnung
    return 4.0  # Beispielwert

def get_job_statistics() -> Dict:
    """Gibt Job-Statistiken zurück"""
    # TODO: Implementierung der Statistik-Berechnung
    return {
        "pending": 0,
        "processing": 0,
        "completed": 0
    }

def get_resource_usage() -> Dict:
    """Gibt Ressourcennutzung zurück"""
    # TODO: Implementierung der Ressourcenüberwachung
    return {
        "cpu": 0,
        "ram": 0,
        "storage": 0
    }

def get_gpu_cost_data() -> List[Dict]:
    """Gibt GPU-Kostendaten zurück"""
    # TODO: Implementierung der Kostenberechnung
    return [] 
import json
import logging
import os
from typing import Dict, List

from data_schema.person_dossier import FaceInstance, PersonDossier
from fastapi import FastAPI, HTTPException

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("person_dossier_service")

app = FastAPI(
    title="Person Dossier Service",
    description="Service für die Verwaltung von Personendossiers",
)


class DossierService:
    def __init__(self):
        self.dossiers: Dict[str, PersonDossier] = {}
        self.load_dossiers()

    def load_dossiers(self):
        """Lädt gespeicherte Dossiers aus der JSON-Datei"""
        try:
            if os.path.exists("data/dossiers.json"):
                with open("data/dossiers.json", "r") as f:
                    data = json.load(f)
                    for dossier_data in data:
                        dossier = PersonDossier(**dossier_data)
                        self.dossiers[dossier.dossier_id] = dossier
                logger.info(f"{len(self.dossiers)} Dossiers geladen")
        except Exception as e:
            logger.error(f"Fehler beim Laden der Dossiers: {str(e)}")

    def save_dossiers(self):
        """Speichert Dossiers in JSON-Datei"""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/dossiers.json", "w") as f:
                json.dump([d.dict() for d in self.dossiers.values()], f, default=str)
            logger.info("Dossiers gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Dossiers: {str(e)}")

    def create_dossier(self, temporary_id: str) -> PersonDossier:
        """Erstellt ein neues Dossier"""
        dossier = PersonDossier(temporary_id=temporary_id)
        self.dossiers[dossier.dossier_id] = dossier
        self.save_dossiers()
        return dossier

    def get_dossier(self, dossier_id: str) -> PersonDossier:
        """Gibt ein Dossier zurück"""
        if dossier_id not in self.dossiers:
            raise HTTPException(status_code=404, detail="Dossier nicht gefunden")
        return self.dossiers[dossier_id]

    def update_dossier(self, dossier_id: str, updates: Dict) -> PersonDossier:
        """Aktualisiert ein Dossier"""
        if dossier_id not in self.dossiers:
            raise HTTPException(status_code=404, detail="Dossier nicht gefunden")

        dossier = self.dossiers[dossier_id]

        if "temporary_id" in updates:
            dossier.temporary_id = updates["temporary_id"]
        if "display_name" in updates:
            dossier.display_name = updates["display_name"]
        if "notes" in updates:
            dossier.notes = updates["notes"]
        if "metadata" in updates:
            dossier.metadata.update(updates["metadata"])

        self.save_dossiers()
        return dossier

    def add_face_instance(
        self, dossier_id: str, face_instance: FaceInstance
    ) -> PersonDossier:
        """Fügt eine Gesichtsinstanz zu einem Dossier hinzu"""
        if dossier_id not in self.dossiers:
            raise HTTPException(status_code=404, detail="Dossier nicht gefunden")

        dossier = self.dossiers[dossier_id]
        dossier.add_face_instance(face_instance)
        self.save_dossiers()
        return dossier

    def list_dossiers(self, skip: int = 0, limit: int = 100) -> List[PersonDossier]:
        """Listet alle Dossiers"""
        return list(self.dossiers.values())[skip : skip + limit]

    def search_dossiers(self, query: str) -> List[PersonDossier]:
        """Sucht nach Dossiers"""
        results = []
        query = query.lower()
        for dossier in self.dossiers.values():
            if (
                query in dossier.temporary_id.lower()
                or (dossier.display_name and query in dossier.display_name.lower())
                or (dossier.notes and query in dossier.notes.lower())
            ):
                results.append(dossier)
        return results


# Service-Instanz erstellen
dossier_service = DossierService()


@app.post("/dossiers", response_model=PersonDossier)
async def create_dossier(temporary_id: str):
    """Erstellt ein neues Dossier"""
    return dossier_service.create_dossier(temporary_id)


@app.get("/dossiers/{dossier_id}", response_model=PersonDossier)
async def get_dossier(dossier_id: str):
    """Gibt ein Dossier zurück"""
    return dossier_service.get_dossier(dossier_id)


@app.put("/dossiers/{dossier_id}", response_model=PersonDossier)
async def update_dossier(dossier_id: str, updates: Dict):
    """Aktualisiert ein Dossier"""
    return dossier_service.update_dossier(dossier_id, updates)


@app.post("/dossiers/{dossier_id}/faces", response_model=PersonDossier)
async def add_face_instance(dossier_id: str, face_instance: FaceInstance):
    """Fügt eine Gesichtsinstanz zu einem Dossier hinzu"""
    return dossier_service.add_face_instance(dossier_id, face_instance)


@app.get("/dossiers", response_model=List[PersonDossier])
async def list_dossiers(skip: int = 0, limit: int = 100):
    """Listet alle Dossiers"""
    return dossier_service.list_dossiers(skip, limit)


@app.get("/dossiers/search", response_model=List[PersonDossier])
async def search_dossiers(query: str):
    """Sucht nach Dossiers"""
    return dossier_service.search_dossiers(query)


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

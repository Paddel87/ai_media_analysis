import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List, Tuple

import clip
import torch
from fastapi import FastAPI, HTTPException
from PIL import Image
from pydantic import BaseModel

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("clip_service")

app = FastAPI(
    title="CLIP Service",
    description="Service für CLIP-basierte Bildanalyse mit GPU-Optimierung",
)


class CLIPService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.preprocess = None
        self.batch_size = 32  # Optimale Batch-Größe für GPU
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.initialize_model()

    def initialize_model(self):
        """Initialisiert das CLIP-Modell"""
        try:
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            # Modell in den Evaluierungsmodus setzen
            self.model.eval()
            # CUDA-Optimierungen aktivieren
            if self.device == "cuda":
                torch.backends.cudnn.benchmark = True
            logger.info(f"CLIP Modell erfolgreich initialisiert auf {self.device}")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren des CLIP Modells: {str(e)}")
            raise

    @lru_cache(maxsize=1000)
    def get_text_embeddings(self, text_queries: Tuple[str, ...]) -> torch.Tensor:
        """Cached Text-Embeddings für häufig verwendete Queries"""
        text_tokens = clip.tokenize(list(text_queries)).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features

    async def process_batch(
        self, images: List[bytes], text_queries: List[str]
    ) -> List[Dict[str, float]]:
        """Verarbeitet einen Batch von Bildern"""
        try:
            # Bilder vorverarbeiten
            image_inputs = []
            for img_data in images:
                image = Image.open(io.BytesIO(img_data))
                image_input = self.preprocess(image)
                image_inputs.append(image_input)

            # Batch erstellen
            batch = torch.stack(image_inputs).to(self.device)

            # Text-Embeddings (gecached)
            text_features = self.get_text_embeddings(tuple(text_queries))

            # CLIP-Vorhersage für Batch
            with torch.no_grad():
                image_features = self.model.encode_image(batch)
                image_features /= image_features.norm(dim=-1, keepdim=True)
                similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

            # Ergebnisse formatieren
            results = []
            for sim_scores in similarity:
                result = {
                    query: float(score)
                    for query, score in zip(text_queries, sim_scores)
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {str(e)}")
            raise

    async def analyze_image(
        self, image_data: bytes, text_queries: List[str]
    ) -> Dict[str, float]:
        """Analysiert ein Bild mit CLIP (asynchron)"""
        try:
            results = await self.process_batch([image_data], text_queries)
            return results[0]
        except Exception as e:
            logger.error(f"Fehler bei der CLIP-Analyse: {str(e)}")
            raise

    async def analyze_batch(
        self, images: List[bytes], text_queries: List[str]
    ) -> List[Dict[str, float]]:
        """Analysiert einen Batch von Bildern"""
        try:
            # Batch in optimale Größen aufteilen
            batches = [
                images[i : i + self.batch_size]
                for i in range(0, len(images), self.batch_size)
            ]

            # Batches parallel verarbeiten
            tasks = [self.process_batch(batch, text_queries) for batch in batches]
            results = await asyncio.gather(*tasks)

            # Ergebnisse zusammenführen
            return [item for sublist in results for item in sublist]

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Analyse: {str(e)}")
            raise

    async def get_image_embedding(self, image_data: bytes) -> List[float]:
        """Extrahiert das Bild-Embedding (asynchron)"""
        try:
            image = Image.open(io.BytesIO(image_data))
            image_input = self.preprocess(image).unsqueeze(0).to(self.device)

            with torch.no_grad():
                image_features = self.model.encode_image(image_input)
                image_features /= image_features.norm(dim=-1, keepdim=True)

            return image_features[0].cpu().numpy().tolist()

        except Exception as e:
            logger.error(f"Fehler beim Extrahieren des Bild-Embeddings: {str(e)}")
            raise


# Service-Instanz erstellen
clip_service = CLIPService()


class ImageAnalysisRequest(BaseModel):
    image_data: bytes
    text_queries: List[str]


class BatchAnalysisRequest(BaseModel):
    images: List[bytes]
    text_queries: List[str]


@app.post("/analyze")
async def analyze_image(request: ImageAnalysisRequest):
    """Analysiert ein Bild mit CLIP"""
    try:
        return await clip_service.analyze_image(
            request.image_data, request.text_queries
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(request: BatchAnalysisRequest):
    """Analysiert einen Batch von Bildern"""
    try:
        return await clip_service.analyze_batch(request.images, request.text_queries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embedding")
async def get_image_embedding(image_data: bytes):
    """Extrahiert das Bild-Embedding"""
    try:
        return {"embedding": await clip_service.get_image_embedding(image_data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "device": clip_service.device,
        "batch_size": clip_service.batch_size,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

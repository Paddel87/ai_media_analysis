from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import anthropic
import google.generativeai as genai
import logging
from typing import List, Dict, Optional, Union
import os
from datetime import datetime
import json
import uuid
from .vector_integration import VectorDBIntegration
from .media_integration import MediaServiceIntegration
from .service_integration import ServiceIntegration

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")

app = FastAPI(
    title="LLM Service",
    description="Service für LLM-Operationen mit OpenAI, Anthropic und Google Gemini"
)

class SafetySettings(BaseModel):
    harassment: str = "block_none"
    hate_speech: str = "block_none"
    sexually_explicit: str = "block_none"
    dangerous_content: str = "block_none"
    disabled: bool = False

class TextGenerationRequest(BaseModel):
    prompt: str
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    context: Optional[List[Dict]] = None
    safety_settings: Optional[SafetySettings] = None

class TextGenerationResponse(BaseModel):
    text: str
    model: str
    usage: Dict
    finish_reason: str
    safety_ratings: Optional[Dict] = None

class EmbeddingRequest(BaseModel):
    text: str
    model: str = "text-embedding-ada-002"

class EmbeddingResponse(BaseModel):
    embedding: List[float]
    model: str
    usage: Dict

class VectorSearchRequest(BaseModel):
    text: str
    limit: int = 5
    score_threshold: float = 0.7
    filter: Optional[Dict] = None

class VectorSearchResponse(BaseModel):
    results: List[Dict]
    query_text: str
    total_results: int

class BatchEmbeddingRequest(BaseModel):
    texts: List[str]
    metadata_list: List[Dict]

class MetadataSearchRequest(BaseModel):
    metadata_filter: Dict
    limit: int = 5

class MetadataUpdateRequest(BaseModel):
    vector_id: str
    new_metadata: Dict

class IndexRequest(BaseModel):
    index_type: str = "HNSW"

class MediaAnalysisRequest(BaseModel):
    media_id: str
    analysis_type: str = "full"
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7

class MediaDescriptionRequest(BaseModel):
    media_id: str
    style: str = "neutral"
    model: str = "gpt-4"
    max_tokens: int = 500
    temperature: float = 0.7

class MediaSearchRequest(BaseModel):
    media_id: str
    limit: int = 5
    model: str = "gpt-4"

class LLMService:
    def __init__(self):
        # OpenAI
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY nicht gesetzt")
        openai.api_key = self.openai_key
        
        # Anthropic
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY nicht gesetzt")
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        
        # Google Gemini
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        if not self.gemini_key:
            raise ValueError("GOOGLE_API_KEY nicht gesetzt")
        genai.configure(api_key=self.gemini_key)
        
        # Service Integration
        self.service_integration = ServiceIntegration({
            "vector_db_url": os.getenv("VECTOR_DB_URL", "http://vector-db:8000"),
            "media_service_url": os.getenv("MEDIA_SERVICE_URL", "http://media-service:8000"),
            "analytics_service_url": os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8000"),
            "cache_service_url": os.getenv("CACHE_SERVICE_URL", "http://cache-service:8000"),
            "monitoring_service_url": os.getenv("MONITORING_SERVICE_URL", "http://monitoring-service:8000")
        })
        
        # Services
        self.vector_db = self.service_integration.get_service("vector_db")
        self.media_service = self.service_integration.get_service("media")
        self.analytics_service = self.service_integration.get_service("analytics")
        self.cache_service = self.service_integration.get_service("cache")
        self.monitoring_service = self.service_integration.get_service("monitoring")
        
    def _get_safety_settings(self, settings: Optional[SafetySettings]) -> Dict:
        """
        Konvertiert Safety Settings in Gemini-Format
        """
        if not settings:
            return {}
            
        # Wenn Safety Settings deaktiviert sind
        if settings.disabled:
            return {
                "harassment": "block_none",
                "hate_speech": "block_none",
                "sexually_explicit": "block_none",
                "dangerous_content": "block_none"
            }
            
        return {
            "harassment": settings.harassment,
            "hate_speech": settings.hate_speech,
            "sexually_explicit": settings.sexually_explicit,
            "dangerous_content": settings.dangerous_content
        }
        
    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        Generiert Text mit dem ausgewählten LLM
        """
        try:
            # Modell-Auswahl
            if request.model.startswith("gpt-"):
                return self._generate_openai(request)
            elif request.model.startswith("claude-"):
                return self._generate_anthropic(request)
            elif request.model.startswith("gemini-"):
                return self._generate_gemini(request)
            else:
                raise ValueError(f"Unbekanntes Modell: {request.model}")
                
        except Exception as e:
            logger.error(f"Fehler bei der Textgenerierung: {str(e)}")
            raise
            
    def _generate_openai(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        Generiert Text mit OpenAI
        """
        messages = []
        
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
            
        if request.context:
            messages.extend(request.context)
            
        messages.append({
            "role": "user",
            "content": request.prompt
        })
        
        response = openai.ChatCompletion.create(
            model=request.model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return TextGenerationResponse(
            text=response.choices[0].message.content,
            model=response.model,
            usage=response.usage,
            finish_reason=response.choices[0].finish_reason
        )
        
    def _generate_anthropic(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        Generiert Text mit Anthropic Claude
        """
        system = request.system_prompt or ""
        
        response = self.anthropic_client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=system,
            messages=[{"role": "user", "content": request.prompt}]
        )
        
        return TextGenerationResponse(
            text=response.content[0].text,
            model=request.model,
            usage={"total_tokens": response.usage.input_tokens + response.usage.output_tokens},
            finish_reason=response.stop_reason
        )
        
    def _generate_gemini(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """
        Generiert Text mit Google Gemini
        """
        model = genai.GenerativeModel(
            model_name=request.model,
            safety_settings=self._get_safety_settings(request.safety_settings)
        )
        
        response = model.generate_content(
            request.prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens
            )
        )
        
        return TextGenerationResponse(
            text=response.text,
            model=request.model,
            usage={"total_tokens": response.candidates[0].token_count},
            finish_reason=response.candidates[0].finish_reason,
            safety_ratings=response.candidates[0].safety_ratings
        )
            
    def create_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Erstellt Embeddings für Text
        """
        try:
            # API-Aufruf
            response = openai.Embedding.create(
                model=request.model,
                input=request.text
            )
            
            # Antwort formatieren
            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model=response.model,
                usage=response.usage
            )
            
        except Exception as e:
            logger.error(f"Fehler bei der Embedding-Erstellung: {str(e)}")
            raise

    def create_embedding_and_store(self, text: str, metadata: Dict) -> bool:
        """
        Erstellt ein Embedding und speichert es in der Vector DB
        """
        try:
            # Embedding erstellen
            embedding_request = EmbeddingRequest(
                text=text,
                model="text-embedding-ada-002"
            )
            
            embedding_response = self.create_embedding(embedding_request)
            
            # In Vector DB speichern
            success = self.vector_db.store_embedding(
                text=text,
                embedding=embedding_response.embedding,
                metadata=metadata
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen und Speichern des Embeddings: {str(e)}")
            raise
            
    def search_similar_texts(self, request: VectorSearchRequest) -> VectorSearchResponse:
        """
        Sucht ähnliche Texte basierend auf Embeddings
        """
        try:
            # Embedding für Suchtext erstellen
            embedding_request = EmbeddingRequest(
                text=request.text,
                model="text-embedding-ada-002"
            )
            
            embedding_response = self.create_embedding(embedding_request)
            
            # Ähnliche Texte suchen
            results = self.vector_db.search_similar(
                embedding=embedding_response.embedding,
                limit=request.limit,
                score_threshold=request.score_threshold
            )
            
            return VectorSearchResponse(
                results=results,
                query_text=request.text,
                total_results=len(results)
            )
            
        except Exception as e:
            logger.error(f"Fehler bei der Ähnlichkeitssuche: {str(e)}")
            raise

    def analyze_media(self, request: MediaAnalysisRequest) -> Dict:
        """
        Analysiert ein Medium mit dem LLM Service
        """
        try:
            # Medium analysieren
            analysis = self.media_service.analyze_media(
                media_id=request.media_id,
                analysis_type=request.analysis_type
            )
            
            if not analysis:
                raise ValueError("Analyse fehlgeschlagen")
                
            # Analyse mit LLM erweitern
            prompt = f"Analysiere das folgende Medium:\n\n{analysis.get('content', '')}"
            
            llm_request = TextGenerationRequest(
                prompt=prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system_prompt="Du bist ein Experte für Medienanalyse."
            )
            
            llm_response = self.generate_text(llm_request)
            
            # Ergebnisse kombinieren
            return {
                "media_id": request.media_id,
                "analysis_type": request.analysis_type,
                "media_analysis": analysis,
                "llm_analysis": llm_response.text,
                "model": request.model
            }
            
        except Exception as e:
            logger.error(f"Fehler bei der Medienanalyse: {str(e)}")
            raise
            
    def generate_media_description(self, request: MediaDescriptionRequest) -> str:
        """
        Generiert eine Beschreibung für ein Medium
        """
        try:
            # Medium abrufen
            media_data = self.media_service.generate_media_description(
                media_id=request.media_id,
                style=request.style
            )
            
            if not media_data:
                raise ValueError("Beschreibung fehlgeschlagen")
                
            # Beschreibung mit LLM generieren
            prompt = f"Generiere eine {request.style} Beschreibung für das folgende Medium:\n\n{media_data}"
            
            llm_request = TextGenerationRequest(
                prompt=prompt,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system_prompt="Du bist ein Experte für Mediendeskription."
            )
            
            llm_response = self.generate_text(llm_request)
            
            return llm_response.text
            
        except Exception as e:
            logger.error(f"Fehler bei der Beschreibungsgenerierung: {str(e)}")
            raise
            
    def search_similar_media(self, request: MediaSearchRequest) -> List[Dict]:
        """
        Sucht ähnliche Medien
        """
        try:
            # Ähnliche Medien suchen
            similar_media = self.media_service.search_similar_media(
                media_id=request.media_id,
                limit=request.limit
            )
            
            if not similar_media:
                return []
                
            # Ähnlichkeiten mit LLM analysieren
            results = []
            
            for media in similar_media:
                prompt = f"Analysiere die Ähnlichkeit zwischen den Medien:\n\nOriginal: {request.media_id}\nVergleich: {media.get('media_id')}"
                
                llm_request = TextGenerationRequest(
                    prompt=prompt,
                    model=request.model,
                    max_tokens=500,
                    temperature=0.5,
                    system_prompt="Du bist ein Experte für Medienvergleich."
                )
                
                llm_response = self.generate_text(llm_request)
                
                results.append({
                    **media,
                    "similarity_analysis": llm_response.text
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei der Mediensuche: {str(e)}")
            raise

# Service-Instanz erstellen
llm_service = LLMService()

@app.post("/generate")
async def generate_text(request: TextGenerationRequest):
    """
    Generiert Text mit dem ausgewählten LLM
    """
    try:
        response = llm_service.generate_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed")
async def create_embedding(request: EmbeddingRequest):
    """
    Erstellt Embeddings für Text
    """
    try:
        response = llm_service.create_embedding(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embed-and-store")
async def create_embedding_and_store(text: str, metadata: Dict):
    """
    Erstellt ein Embedding und speichert es in der Vector DB
    """
    try:
        success = llm_service.create_embedding_and_store(text, metadata)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-similar")
async def search_similar_texts(request: VectorSearchRequest):
    """
    Sucht ähnliche Texte basierend auf Embeddings
    """
    try:
        results = llm_service.search_similar_texts(request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-media")
async def analyze_media(request: MediaAnalysisRequest):
    """
    Analysiert ein Medium mit dem LLM Service
    """
    try:
        analysis = llm_service.analyze_media(request)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/describe-media")
async def generate_media_description(request: MediaDescriptionRequest):
    """
    Generiert eine Beschreibung für ein Medium
    """
    try:
        description = llm_service.generate_media_description(request)
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-similar-media")
async def search_similar_media(request: MediaSearchRequest):
    """
    Sucht ähnliche Medien
    """
    try:
        results = llm_service.search_similar_media(request)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-embed")
async def batch_store_embeddings(request: BatchEmbeddingRequest):
    """
    Speichert mehrere Embeddings in der Vector DB
    """
    try:
        # Embeddings erstellen
        embeddings = []
        for text in request.texts:
            embedding_request = EmbeddingRequest(
                text=text,
                model="text-embedding-ada-002"
            )
            embedding_response = llm_service.create_embedding(embedding_request)
            embeddings.append(embedding_response.embedding)
        
        # Batch speichern
        results = llm_service.vector_db.batch_store_embeddings(
            texts=request.texts,
            embeddings=embeddings,
            metadata_list=request.metadata_list
        )
        
        return {"success": all(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-metadata")
async def search_by_metadata(request: MetadataSearchRequest):
    """
    Sucht Embeddings nach Metadaten
    """
    try:
        results = llm_service.vector_db.search_by_metadata(
            metadata_filter=request.metadata_filter,
            limit=request.limit
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/update-metadata")
async def update_metadata(request: MetadataUpdateRequest):
    """
    Aktualisiert die Metadaten eines Embeddings
    """
    try:
        success = llm_service.vector_db.update_metadata(
            vector_id=request.vector_id,
            new_metadata=request.new_metadata
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collection-stats")
async def get_collection_stats():
    """
    Gibt Statistiken über die Collection zurück
    """
    try:
        stats = llm_service.vector_db.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-index")
async def create_index(request: IndexRequest):
    """
    Erstellt einen Index für die Collection
    """
    try:
        success = llm_service.vector_db.create_index(
            index_type=request.index_type
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collection")
async def delete_collection():
    """
    Löscht die Collection
    """
    try:
        success = llm_service.vector_db.delete_collection()
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # OpenAI testen
        openai_models = openai.Model.list()
        
        # Anthropic testen
        anthropic_models = llm_service.anthropic_client.models.list()
        
        # Gemini testen
        gemini_models = genai.list_models()
        
        return {
            "status": "healthy",
            "openai_models": len(openai_models.data),
            "anthropic_models": len(anthropic_models),
            "gemini_models": len(gemini_models),
            "api_keys_valid": {
                "openai": True,
                "anthropic": True,
                "gemini": True
            }
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/vector-health")
async def vector_health_check():
    """
    Health Check für Vector DB Integration
    """
    try:
        health = llm_service.vector_db.get_health()
        return health
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/media-health")
async def media_health_check():
    """
    Health Check für Media Service Integration
    """
    try:
        health = llm_service.media_service.get_health()
        return health
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/services-health")
async def services_health_check():
    """
    Health Check für alle Services
    """
    try:
        health = llm_service.service_integration.get_health()
        return health
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/analytics/embedding/{embedding_id}")
async def get_embedding_stats(embedding_id: str):
    """
    Gibt Statistiken für ein Embedding zurück
    """
    try:
        stats = llm_service.analytics_service.get_embedding_stats(embedding_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/metrics/{service}")
async def get_service_metrics(service: str):
    """
    Gibt Metriken für einen Service zurück
    """
    try:
        metrics = llm_service.monitoring_service.get_service_metrics(service)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
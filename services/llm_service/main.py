from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import logging
from typing import List, Dict, Optional, Union, Any
import os
from datetime import datetime
import json
import uuid
import redis
import pickle
from functools import lru_cache
import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai
from anthropic import Anthropic

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm_service")

app = FastAPI(
    title="LLM Service",
    description="Service für verschiedene LLM-Anbieter und lokale Modelle"
)

# Redis-Konfiguration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Thread Pool für CPU-intensive Operationen
thread_pool = ThreadPoolExecutor(max_workers=4)

class LLMRequest(BaseModel):
    prompt: str
    provider: str = "gemini"  # gemini, openai, anthropic, local
    model: str = "gemini-pro"  # gemini-pro, gpt-4, claude-3-opus, mistral-7b, etc.
    temperature: float = 0.7
    max_tokens: int = 1000
    safety_settings: Optional[Dict] = None
    system_prompt: Optional[str] = None
    stream: bool = False

class LLMResponse(BaseModel):
    text: str
    provider: str
    model: str
    usage: Optional[Dict] = None
    safety_ratings: Optional[Dict] = None

class LLMService:
    def __init__(self):
        # Redis-Verbindung
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )
        
        # API-Keys laden
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Gemini konfigurieren
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            
        # OpenAI konfigurieren
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            
        # Anthropic konfigurieren
        if self.anthropic_api_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_api_key)
            
        # Lokale Modelle laden
        self.local_models = {}
        self._load_local_models()
        
    def _load_local_models(self):
        """
        Lädt lokale Modelle
        """
        try:
            # Mistral 7B
            if torch.cuda.is_available():
                model_id = "mistralai/Mistral-7B-v0.1"
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                self.local_models["mistral-7b"] = {
                    "model": model,
                    "tokenizer": tokenizer
                }
                
            # Nous-Hermes-2
            if torch.cuda.is_available():
                model_id = "NousResearch/Nous-Hermes-2-7B"
                tokenizer = AutoTokenizer.from_pretrained(model_id)
                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                self.local_models["nous-hermes-2"] = {
                    "model": model,
                    "tokenizer": tokenizer
                }
                
        except Exception as e:
            logger.error(f"Fehler beim Laden der lokalen Modelle: {str(e)}")
            
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_text(self, request: LLMRequest) -> LLMResponse:
        """
        Generiert Text mit dem gewählten LLM
        """
        try:
            # Cache-Key generieren
            cache_key = f"llm:{request.provider}:{request.model}:{hash(str(request.dict()))}"
            
            # Cache prüfen
            cached_response = self.redis_client.get(cache_key)
            if cached_response:
                return pickle.loads(cached_response)
                
            # Text generieren
            if request.provider == "gemini":
                response = await self._generate_gemini(request)
            elif request.provider == "openai":
                response = await self._generate_openai(request)
            elif request.provider == "anthropic":
                response = await self._generate_anthropic(request)
            elif request.provider == "local":
                response = await self._generate_local(request)
            else:
                raise ValueError(f"Unbekannter Provider: {request.provider}")
                
            # Cache speichern
            self.redis_client.set(cache_key, pickle.dumps(response))
            
            return response
            
        except Exception as e:
            logger.error(f"Fehler bei der Textgenerierung: {str(e)}")
            raise
            
    async def _generate_gemini(self, request: LLMRequest) -> LLMResponse:
        """
        Generiert Text mit Gemini
        """
        try:
            # Safety Settings
            safety_settings = request.safety_settings or {
                "HARASSMENT": "block_none",
                "HATE_SPEECH": "block_none",
                "SEXUALLY_EXPLICIT": "block_none",
                "DANGEROUS_CONTENT": "block_none"
            }
            
            # Model initialisieren
            model = genai.GenerativeModel(
                model_name=request.model,
                safety_settings=safety_settings
            )
            
            # Text generieren
            response = await model.generate_content_async(
                request.prompt,
                generation_config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens
                }
            )
            
            return LLMResponse(
                text=response.text,
                provider="gemini",
                model=request.model,
                safety_ratings=response.safety_ratings
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Gemini-Generierung: {str(e)}")
            raise
            
    async def _generate_openai(self, request: LLMRequest) -> LLMResponse:
        """
        Generiert Text mit OpenAI
        """
        try:
            # Text generieren
            response = await openai.ChatCompletion.acreate(
                model=request.model,
                messages=[
                    {"role": "system", "content": request.system_prompt or "Du bist ein hilfreicher Assistent."},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
            
            return LLMResponse(
                text=response.choices[0].message.content,
                provider="openai",
                model=request.model,
                usage=response.usage
            )
            
        except Exception as e:
            logger.error(f"Fehler bei OpenAI-Generierung: {str(e)}")
            raise
            
    async def _generate_anthropic(self, request: LLMRequest) -> LLMResponse:
        """
        Generiert Text mit Anthropic
        """
        try:
            # Text generieren
            response = await self.anthropic_client.messages.create(
                model=request.model,
                messages=[
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                system=request.system_prompt
            )
            
            return LLMResponse(
                text=response.content[0].text,
                provider="anthropic",
                model=request.model
            )
            
        except Exception as e:
            logger.error(f"Fehler bei Anthropic-Generierung: {str(e)}")
            raise
            
    async def _generate_local(self, request: LLMRequest) -> LLMResponse:
        """
        Generiert Text mit lokalem Modell
        """
        try:
            # Modell prüfen
            if request.model not in self.local_models:
                raise ValueError(f"Lokales Modell {request.model} nicht verfügbar")
                
            model_data = self.local_models[request.model]
            
            # Text generieren
            inputs = model_data["tokenizer"](
                request.prompt,
                return_tensors="pt",
                padding=True
            ).to(model_data["model"].device)
            
            outputs = model_data["model"].generate(
                **inputs,
                max_length=request.max_tokens,
                temperature=request.temperature,
                do_sample=True
            )
            
            text = model_data["tokenizer"].decode(outputs[0], skip_special_tokens=True)
            
            return LLMResponse(
                text=text,
                provider="local",
                model=request.model
            )
            
        except Exception as e:
            logger.error(f"Fehler bei lokaler Generierung: {str(e)}")
            raise

# Service-Instanz erstellen
llm_service = LLMService()

@app.post("/generate")
async def generate_text(request: LLMRequest):
    """
    Generiert Text mit dem gewählten LLM
    """
    try:
        response = await llm_service.generate_text(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health Check Endpoint
    """
    try:
        # Redis-Verbindung testen
        redis_healthy = llm_service.redis_client.ping()
        
        # Verfügbare Modelle prüfen
        available_models = {
            "gemini": bool(llm_service.gemini_api_key),
            "openai": bool(llm_service.openai_api_key),
            "anthropic": bool(llm_service.anthropic_api_key),
            "local": list(llm_service.local_models.keys())
        }
        
        return {
            "status": "healthy" if redis_healthy else "unhealthy",
            "redis": "available" if redis_healthy else "unavailable",
            "available_models": available_models
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
import asyncio
import gc
import math
import os
import pickle
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

import aiohttp
import cv2
import librosa
import numpy as np
import redis
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import (
    CLIPModel,
    CLIPProcessor,
    WhisperForConditionalGeneration,
    WhisperProcessor,
)
from PIL import Image

# Lokale Imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.logging_config import ServiceLogger

# Logger initialisieren
logger = ServiceLogger("restraint_detection")

app = FastAPI(
    title="Restraint Detection Service",
    description="Service zur Erkennung von Fesselungen und verwandten Materialien in Bildern und Videos",
    version="1.0.0",
)


class InstanceProvider:
    """Klasse zur Verwaltung von Cloud-Instanzen und Preisen."""

    def __init__(self):
        self.providers = {
            "vast_ai": {
                "api_url": "https://vast.ai/api/v0/bundles/",
                "regions": ["global"],
                "instance_types": [
                    # High-End GPUs für CLIP und Whisper
                    "RTX 3090",
                    "RTX 4090",
                    "A100",
                    "A6000",
                    "V100",
                    # Mid-Range GPUs für CLIP
                    "RTX 3080",
                    "RTX 4080",
                    "A5000",
                    "A4000",
                    # Entry-Level GPUs für CLIP
                    "RTX 3070",
                    "RTX 4070",
                    "A3000",
                    # Spezielle Instanzen für Whisper
                    "T4",
                    "P100",
                    "K80",
                ],
            },
            "aws": {
                "api_url": "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json",
                "regions": ["eu-central-1", "us-east-1"],
                "instance_types": ["g4dn.xlarge", "g4dn.2xlarge", "p3.2xlarge"],
            },
            "gcp": {
                "api_url": "https://cloudpricingcalculator.appspot.com/static/data/pricelist.json",
                "regions": ["europe-west4", "us-central1"],
                "instance_types": ["n1-standard-4", "n1-standard-8"],
            },
            "azure": {
                "api_url": "https://prices.azure.com/api/retail/prices",
                "regions": ["westeurope", "eastus"],
                "instance_types": ["Standard_NC6", "Standard_NC12"],
            },
        }

        self.instance_specs = {
            # High-End GPUs
            "RTX 3090": {
                "gpu_memory": 24,
                "compute_units": 2,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.0,
            },
            "RTX 4090": {
                "gpu_memory": 24,
                "compute_units": 2.5,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.2,
            },
            "A100": {
                "gpu_memory": 40,
                "compute_units": 3,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.5,
            },
            "A6000": {
                "gpu_memory": 48,
                "compute_units": 2.5,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.3,
            },
            "V100": {
                "gpu_memory": 32,
                "compute_units": 2,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.1,
            },
            # Mid-Range GPUs
            "RTX 3080": {
                "gpu_memory": 10,
                "compute_units": 1.8,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 0.9,
            },
            "RTX 4080": {
                "gpu_memory": 16,
                "compute_units": 2.0,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 1.0,
            },
            "A5000": {
                "gpu_memory": 24,
                "compute_units": 2.0,
                "provider": "vast_ai",
                "models": ["clip", "whisper"],
                "performance_rating": 1.1,
            },
            "A4000": {
                "gpu_memory": 16,
                "compute_units": 1.8,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 0.9,
            },
            # Entry-Level GPUs
            "RTX 3070": {
                "gpu_memory": 8,
                "compute_units": 1.5,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 0.8,
            },
            "RTX 4070": {
                "gpu_memory": 12,
                "compute_units": 1.7,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 0.85,
            },
            "A3000": {
                "gpu_memory": 12,
                "compute_units": 1.6,
                "provider": "vast_ai",
                "models": ["clip"],
                "performance_rating": 0.8,
            },
            # Spezielle Instanzen für Whisper
            "T4": {
                "gpu_memory": 16,
                "compute_units": 1.0,
                "provider": "vast_ai",
                "models": ["whisper"],
                "performance_rating": 0.7,
            },
            "P100": {
                "gpu_memory": 16,
                "compute_units": 1.2,
                "provider": "vast_ai",
                "models": ["whisper"],
                "performance_rating": 0.8,
            },
            "K80": {
                "gpu_memory": 24,
                "compute_units": 0.9,
                "provider": "vast_ai",
                "models": ["whisper"],
                "performance_rating": 0.6,
            },
            # Bestehende Instanzen
            "g4dn.xlarge": {
                "gpu_memory": 16,
                "compute_units": 1,
                "provider": "aws",
                "models": ["clip", "whisper"],
                "performance_rating": 0.8,
            },
            "g4dn.2xlarge": {
                "gpu_memory": 32,
                "compute_units": 2,
                "provider": "aws",
                "models": ["clip", "whisper"],
                "performance_rating": 1.0,
            },
            "p3.2xlarge": {
                "gpu_memory": 16,
                "compute_units": 1,
                "provider": "aws",
                "models": ["clip", "whisper"],
                "performance_rating": 0.9,
            },
            "n1-standard-4": {
                "gpu_memory": 16,
                "compute_units": 1,
                "provider": "gcp",
                "models": ["clip", "whisper"],
                "performance_rating": 0.8,
            },
            "n1-standard-8": {
                "gpu_memory": 32,
                "compute_units": 2,
                "provider": "gcp",
                "models": ["clip", "whisper"],
                "performance_rating": 1.0,
            },
            "Standard_NC6": {
                "gpu_memory": 16,
                "compute_units": 1,
                "provider": "azure",
                "models": ["clip", "whisper"],
                "performance_rating": 0.8,
            },
            "Standard_NC12": {
                "gpu_memory": 32,
                "compute_units": 2,
                "provider": "azure",
                "models": ["clip", "whisper"],
                "performance_rating": 1.0,
            },
        }

        # Modell-Ressourcenanforderungen
        self.model_requirements = {
            "clip": {
                "min_memory": 6,  # GB - Reduziert aufgrund von Optimierungen
                "min_compute": 0.8,
                "parallel_factor": 0.95,  # Erhöht aufgrund von effizienter GPU-Nutzung
                "spin_up_time": 3,  # Reduziert durch optimierte Modellladung
                "memory_scaling": 0.7,  # Speicherbedarf pro zusätzlicher Instanz
                "compute_scaling": 0.8,  # Compute-Bedarf pro zusätzlicher Instanz
            },
            "whisper": {
                "min_memory": 8,  # GB - Reduziert durch Quantisierung
                "min_compute": 1.0,
                "parallel_factor": 0.85,  # Erhöht durch Batch-Verarbeitung
                "spin_up_time": 5,
                "memory_scaling": 0.75,
                "compute_scaling": 0.85,
            },
        }

        # Batch-Verarbeitungszeiten mit Skalierungseffekten
        self.batch_times = {
            "clip": {
                "small": 0.15,  # Sekunden pro Frame
                "medium": 0.12,
                "large": 0.10,
                "scaling_factor": 0.9,  # Verbesserung bei größeren Batches
                "parallel_boost": 0.85,  # Zusätzliche Verbesserung bei Parallelisierung
            },
            "whisper": {
                "small": 0.25,  # Sekunden pro Audio-Segment
                "medium": 0.20,
                "large": 0.15,
                "scaling_factor": 0.85,
                "parallel_boost": 0.8,
            },
        }

    async def fetch_prices(self) -> Dict[str, Dict[str, Any]]:
        """Holt aktuelle Preise von allen Providern."""
        prices = {}
        async with aiohttp.ClientSession() as session:
            for provider, config in self.providers.items():
                try:
                    if provider == "vast_ai":
                        prices[provider] = await self._fetch_vast_ai_prices(session)
                    else:
                        async with session.get(config["api_url"]) as response:
                            if response.status == 200:
                                data = await response.json()
                                prices[provider] = self._parse_prices(provider, data)
                except Exception as e:
                    logger.log_error(
                        f"Fehler beim Abrufen der Preise von {provider}", error=e
                    )
        return prices

    async def _fetch_vast_ai_prices(
        self, session: aiohttp.ClientSession
    ) -> Dict[str, Any]:
        """Holt aktuelle Preise von Vast.ai."""
        try:
            async with session.get(self.providers["vast_ai"]["api_url"]) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_vast_ai_prices(data)
                return {}
        except Exception as e:
            logger.log_error("Fehler beim Abrufen der Vast.ai Preise", error=e)
            return {}

    def _parse_vast_ai_prices(self, data: Dict) -> Dict[str, Any]:
        """Parst die Preisdaten von Vast.ai."""
        prices = {}
        try:
            for instance in self.providers["vast_ai"]["instance_types"]:
                # Filtere nach GPU-Typ
                matching_offers = [
                    offer
                    for offer in data.get("offers", [])
                    if instance in offer.get("gpu_name", "")
                ]

                if matching_offers:
                    # Berechne Durchschnittspreis
                    avg_price = sum(
                        float(offer.get("dph_total", 0))  # Dollar pro Stunde
                        for offer in matching_offers
                    ) / len(matching_offers)

                    prices[instance] = {
                        "on_demand": {"global": avg_price},
                        "spot": {
                            "global": avg_price * 0.7
                        },  # Vast.ai bietet oft Rabatte
                        "specs": self.instance_specs[instance],
                        "reliability_score": self._calculate_vast_reliability(
                            matching_offers
                        ),
                    }
        except Exception as e:
            logger.log_error("Fehler beim Parsen der Vast.ai Preise", error=e)

        return prices

    def _calculate_vast_reliability(self, offers: List[Dict]) -> float:
        """Berechnet einen Zuverlässigkeits-Score für Vast.ai Angebote."""
        try:
            if not offers:
                return 0.0

            # Faktoren für Zuverlässigkeit
            reliability_factors = {
                "reliability": 0.4,  # Gewichtung für Zuverlässigkeitswert
                "num_offers": 0.3,  # Gewichtung für Anzahl der Angebote
                "uptime": 0.3,  # Gewichtung für Uptime
            }

            # Berechne Durchschnittszuverlässigkeit
            avg_reliability = sum(
                float(offer.get("reliability", 0)) for offer in offers
            ) / len(offers)

            # Berechne Durchschnittsuptime
            avg_uptime = sum(float(offer.get("uptime", 0)) for offer in offers) / len(
                offers
            )

            # Normalisiere Anzahl der Angebote (max 10 Angebote = 1.0)
            num_offers_score = min(len(offers) / 10, 1.0)

            # Berechne Gesamtscore
            total_score = (
                reliability_factors["reliability"] * avg_reliability
                + reliability_factors["num_offers"] * num_offers_score
                + reliability_factors["uptime"] * avg_uptime
            )

            return round(total_score, 2)

        except Exception as e:
            logger.log_error(
                "Fehler bei der Berechnung des Vast.ai Zuverlässigkeits-Scores", error=e
            )
            return 0.0

    def _parse_prices(self, provider: str, data: Dict) -> Dict[str, Any]:
        """Parst die Preisdaten des jeweiligen Providers."""
        prices = {}
        if provider == "aws":
            for instance in self.providers[provider]["instance_types"]:
                prices[instance] = {
                    "on_demand": self._extract_aws_price(data, instance, "OnDemand"),
                    "spot": self._extract_aws_price(data, instance, "Spot"),
                    "specs": self.instance_specs[instance],
                }
        # Ähnliche Implementierung für GCP und Azure
        return prices

    def _extract_aws_price(
        self, data: Dict, instance: str, price_type: str
    ) -> Dict[str, float]:
        """Extrahiert AWS-Preise aus der API-Antwort."""
        prices = {}
        for region in self.providers["aws"]["regions"]:
            try:
                if price_type == "OnDemand":
                    price = data["terms"]["OnDemand"][f"{instance}.{region}"][
                        "priceDimensions"
                    ][0]["pricePerUnit"]["USD"]
                else:
                    price = data["terms"]["Spot"][f"{instance}.{region}"][
                        "priceDimensions"
                    ][0]["pricePerUnit"]["USD"]
                prices[region] = float(price)
            except KeyError:
                prices[region] = None
        return prices

    def _calculate_parallel_capacity(
        self, specs: Dict[str, Any], models: List[str]
    ) -> Dict[str, Any]:
        """
        Berechnet die parallele Ausführungskapazität einer Instanz mit Skalierungseffekten.
        """
        try:
            total_memory = specs["gpu_memory"]
            total_compute = specs["compute_units"]

            # Berechne maximale parallele Ausführung
            max_parallel = {"clip": 0, "whisper": 0}

            # Berechne für jedes Modell
            for model in models:
                req = self.model_requirements[model]

                # Berechne basierend auf Speicher mit Skalierungseffekt
                memory_based = 1
                remaining_memory = total_memory - req["min_memory"]
                while remaining_memory >= req["min_memory"] * req["memory_scaling"]:
                    memory_based += 1
                    remaining_memory -= req["min_memory"] * req["memory_scaling"]

                # Berechne basierend auf Compute mit Skalierungseffekt
                compute_based = 1
                remaining_compute = total_compute - req["min_compute"]
                while remaining_compute >= req["min_compute"] * req["compute_scaling"]:
                    compute_based += 1
                    remaining_compute -= req["min_compute"] * req["compute_scaling"]

                max_parallel[model] = min(memory_based, compute_based)

            return max_parallel

        except Exception as e:
            logger.log_error(
                "Fehler bei der Berechnung der parallelen Kapazität", error=e
            )
            return {"clip": 1, "whisper": 1}

    def _calculate_effective_processing_time(
        self,
        processing_time: float,
        models: List[str],
        parallel_capacity: Dict[str, int],
    ) -> float:
        """
        Berechnet die effektive Verarbeitungszeit unter Berücksichtigung von Parallelisierung und Skalierungseffekten.
        """
        try:
            # Basis-Verarbeitungszeit
            base_time = processing_time

            # Spin-up-Zeiten (nur einmal pro Modell)
            spin_up_time = sum(
                self.model_requirements[model]["spin_up_time"] for model in models
            )

            # Parallele Verarbeitung mit Skalierungseffekten
            parallel_time = base_time
            for model in models:
                if parallel_capacity[model] > 1:
                    # Reduziere Zeit basierend auf Parallelisierungsfaktor und Skalierungseffekten
                    parallel_factor = self.model_requirements[model]["parallel_factor"]
                    scaling_factor = self.batch_times[model]["scaling_factor"]
                    parallel_boost = self.batch_times[model]["parallel_boost"]

                    # Berechne effektive Zeitreduktion
                    time_reduction = (1 / parallel_capacity[model]) * parallel_factor
                    scaling_reduction = scaling_factor ** (parallel_capacity[model] - 1)
                    parallel_boost_reduction = parallel_boost ** (
                        parallel_capacity[model] - 1
                    )

                    parallel_time *= (
                        time_reduction * scaling_reduction * parallel_boost_reduction
                    )

            return spin_up_time + parallel_time

        except Exception as e:
            logger.log_error(
                "Fehler bei der Berechnung der effektiven Verarbeitungszeit", error=e
            )
            return processing_time

    def calculate_price_performance(
        self, prices: Dict[str, Dict[str, Any]], processing_time: float
    ) -> List[Dict[str, Any]]:
        """Berechnet Preis/Leistungsverhältnis für alle Instanzen."""
        results = []
        for provider, instances in prices.items():
            for instance, data in instances.items():
                specs = data["specs"]
                for region, on_demand_price in data["on_demand"].items():
                    if on_demand_price:
                        spot_price = data["spot"].get(region)

                        # Berechne parallele Kapazität
                        parallel_capacity = self._calculate_parallel_capacity(
                            specs, specs["models"]
                        )

                        # Berechne effektive Verarbeitungszeit
                        effective_time = self._calculate_effective_processing_time(
                            processing_time, specs["models"], parallel_capacity
                        )

                        # Basis-Ergebnis
                        result = {
                            "provider": provider,
                            "instance": instance,
                            "region": region,
                            "on_demand_cost": round(
                                on_demand_price * effective_time / 3600, 4
                            ),
                            "spot_cost": (
                                round(spot_price * effective_time / 3600, 4)
                                if spot_price
                                else None
                            ),
                            "performance_score": specs["compute_units"]
                            / on_demand_price,
                            "memory_score": specs["gpu_memory"] / on_demand_price,
                            "specs": specs,
                            "supported_models": specs["models"],
                            "performance_rating": specs["performance_rating"],
                            "parallel_capacity": parallel_capacity,
                            "effective_processing_time": round(effective_time, 2),
                            "cost_efficiency": round(
                                (specs["compute_units"] * specs["gpu_memory"])
                                / (on_demand_price * effective_time / 3600),
                                2,
                            ),
                        }

                        # Vast.ai spezifische Informationen
                        if provider == "vast_ai":
                            result["reliability_score"] = data.get(
                                "reliability_score", 0.0
                            )
                            # Berücksichtige Zuverlässigkeit und Performance-Rating
                            result["performance_score"] *= (
                                1 + result["reliability_score"]
                            ) * specs["performance_rating"]

                        results.append(result)

        # Sortiere nach Kosteneffizienz, Gesamtkosten und Modellunterstützung
        return sorted(
            results,
            key=lambda x: (
                -x["cost_efficiency"],  # Primär nach Kosteneffizienz
                x["on_demand_cost"],  # Sekundär nach Gesamtkosten
                -len(x["supported_models"]),  # Tertiär nach Modellunterstützung
            ),
        )


class InstanceManager:
    """Verwaltet mehrere GPU-Instanzen und deren Lastverteilung."""

    def __init__(self):
        self.active_instances = {}  # Dict[str, Dict] - Aktive Instanzen
        self.instance_provider = InstanceProvider()
        self.max_instances = 5  # Maximale Anzahl paralleler Instanzen
        self.min_utilization = 0.7  # Minimale Auslastung für neue Instanz
        self.max_utilization = 0.9  # Maximale Auslastung vor Skalierung

        # API-Konfiguration
        self.api_config = {
            "vast_ai": {
                "api_key": os.getenv("VAST_AI_API_KEY"),
                "base_url": "https://vast.ai/api/v0",
                "endpoints": {
                    "create": "/asks/create/",
                    "destroy": "/instances/{instance_id}/destroy/",
                    "status": "/instances/{instance_id}/status/",
                    "ssh": "/instances/{instance_id}/ssh/",
                },
            }
        }

        # SSH-Konfiguration
        self.ssh_config = {
            "key_path": os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa"),
            "username": "root",
            "port": 22,
        }

        # Instanz-Status
        self.instance_states = {
            "creating": "Wird erstellt",
            "running": "Läuft",
            "stopping": "Wird gestoppt",
            "stopped": "Gestoppt",
            "error": "Fehler",
        }

    async def get_optimal_instance_config(
        self, processing_time: float, required_models: List[str], current_load: float
    ) -> Dict[str, Any]:
        """
        Bestimmt die optimale Instanzkonfiguration basierend auf Anforderungen und Last.
        """
        try:
            # Hole aktuelle Preise
            prices = await self.instance_provider.fetch_prices()

            # Berechne benötigte Kapazität
            required_capacity = self._calculate_required_capacity(
                processing_time, required_models, current_load
            )

            # Bestimme optimale Instanzanzahl
            instance_count = self._calculate_optimal_instance_count(
                required_capacity, current_load
            )

            # Finde beste Instanzkonfiguration
            instance_config = self._find_best_instance_config(
                prices, instance_count, required_models
            )

            return {
                "instance_count": instance_count,
                "instance_type": instance_config["instance_type"],
                "provider": instance_config["provider"],
                "estimated_cost": instance_config["total_cost"],
                "estimated_processing_time": instance_config["effective_time"],
                "scaling_factor": instance_config["scaling_factor"],
            }

        except Exception as e:
            logger.log_error(
                "Fehler bei der Berechnung der optimalen Instanzkonfiguration", error=e
            )
            raise

    def _calculate_required_capacity(
        self, processing_time: float, required_models: List[str], current_load: float
    ) -> float:
        """Berechnet die benötigte Kapazität basierend auf Anforderungen."""
        try:
            # Basis-Kapazität
            base_capacity = processing_time * (1 + current_load)

            # Modell-spezifische Anforderungen
            model_capacity = sum(
                self.instance_provider.model_requirements[model]["min_compute"]
                for model in required_models
            )

            return base_capacity * model_capacity

        except Exception as e:
            logger.log_error("Fehler bei der Kapazitätsberechnung", error=e)
            return processing_time

    def _calculate_optimal_instance_count(
        self, required_capacity: float, current_load: float
    ) -> int:
        """Berechnet die optimale Anzahl von Instanzen."""
        try:
            # Berechne basierend auf Last und Kapazität
            if current_load >= self.max_utilization:
                return min(
                    math.ceil(required_capacity / self.min_utilization),
                    self.max_instances,
                )
            elif current_load <= self.min_utilization:
                return 1
            else:
                return min(
                    math.ceil(required_capacity / current_load), self.max_instances
                )

        except Exception as e:
            logger.log_error("Fehler bei der Berechnung der Instanzanzahl", error=e)
            return 1

    def _find_best_instance_config(
        self,
        prices: Dict[str, Dict[str, Any]],
        instance_count: int,
        required_models: List[str],
    ) -> Dict[str, Any]:
        """Findet die beste Instanzkonfiguration für die Anforderungen."""
        try:
            best_config = None
            best_cost = float("inf")

            for provider, instances in prices.items():
                for instance, data in instances.items():
                    specs = data["specs"]

                    # Prüfe Modellunterstützung
                    if not all(model in specs["models"] for model in required_models):
                        continue

                    # Berechne effektive Verarbeitungszeit
                    parallel_capacity = (
                        self.instance_provider._calculate_parallel_capacity(
                            specs, required_models
                        )
                    )

                    effective_time = (
                        self.instance_provider._calculate_effective_processing_time(
                            1.0, required_models, parallel_capacity  # Basis-Zeit
                        )
                    )

                    # Berechne Gesamtkosten
                    total_cost = data["on_demand"]["global"] * instance_count

                    # Berechne Skalierungsfaktor
                    scaling_factor = 1.0
                    for model in required_models:
                        if parallel_capacity[model] > 1:
                            scaling_factor *= (
                                self.instance_provider.model_requirements[model][
                                    "parallel_factor"
                                ]
                                * self.instance_provider.batch_times[model][
                                    "scaling_factor"
                                ]
                                * self.instance_provider.batch_times[model][
                                    "parallel_boost"
                                ]
                            )

                    # Aktualisiere beste Konfiguration
                    if total_cost < best_cost:
                        best_config = {
                            "instance_type": instance,
                            "provider": provider,
                            "total_cost": total_cost,
                            "effective_time": effective_time,
                            "scaling_factor": scaling_factor,
                            "parallel_capacity": parallel_capacity,
                        }
                        best_cost = total_cost

            return best_config

        except Exception as e:
            logger.log_error(
                "Fehler bei der Suche nach der besten Instanzkonfiguration", error=e
            )
            raise

    async def scale_instances(self, current_load: float) -> Dict[str, Any]:
        """
        Skaliert die Instanzen basierend auf der aktuellen Last.
        """
        try:
            if current_load >= self.max_utilization:
                # Skaliere hoch
                return await self._scale_up()
            elif current_load <= self.min_utilization:
                # Skaliere runter
                return await self._scale_down()
            else:
                return {"action": "maintain", "reason": "Last im optimalen Bereich"}

        except Exception as e:
            logger.log_error("Fehler beim Skalieren der Instanzen", error=e)
            raise

    async def _create_vast_instance(self, instance_type: str) -> Dict[str, Any]:
        """
        Erstellt eine neue Instanz bei Vast.ai.
        """
        try:
            if not self.api_config["vast_ai"]["api_key"]:
                raise ValueError("Vast.ai API-Key nicht konfiguriert")

            # Hole verfügbare Angebote
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_config['vast_ai']['api_key']}"
                }

                # Suche nach passendem Angebot
                search_url = f"{self.api_config['vast_ai']['base_url']}/bundles/"
                async with session.get(search_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Abrufen der Angebote: {response.status}"
                        )

                    offers = await response.json()

                    # Filtere nach GPU-Typ und Verfügbarkeit
                    matching_offers = [
                        offer
                        for offer in offers.get("offers", [])
                        if instance_type in offer.get("gpu_name", "")
                        and offer.get("reliability", 0) > 0.8
                        and offer.get("num_gpus", 0) > 0
                    ]

                    if not matching_offers:
                        raise Exception(
                            f"Keine passenden Angebote für {instance_type} gefunden"
                        )

                    # Wähle bestes Angebot
                    best_offer = min(
                        matching_offers,
                        key=lambda x: float(x.get("dph_total", float("inf"))),
                    )

                    # Erstelle Instanz
                    create_url = f"{self.api_config['vast_ai']['base_url']}{self.api_config['vast_ai']['endpoints']['create']}"
                    create_data = {
                        "client_id": best_offer["client_id"],
                        "price": best_offer["dph_total"],
                        "image": "nvidia/cuda:11.8.0-runtime-ubuntu22.04",
                        "onstart": """
                            apt-get update && apt-get install -y python3-pip
                            pip3 install torch torchvision torchaudio
                            pip3 install transformers
                            pip3 install fastapi uvicorn
                        """,
                        "env": {"PYTHONUNBUFFERED": "1", "CUDA_VISIBLE_DEVICES": "0"},
                    }

                    async with session.post(
                        create_url, headers=headers, json=create_data
                    ) as response:
                        if response.status != 200:
                            raise Exception(
                                f"Fehler beim Erstellen der Instanz: {response.status}"
                            )

                        instance_data = await response.json()

                        # Warte auf SSH-Verfügbarkeit
                        instance_id = instance_data["instance_id"]
                        ssh_info = await self._wait_for_ssh(instance_id)

                        return {
                            "instance_id": instance_id,
                            "provider": "vast_ai",
                            "instance_type": instance_type,
                            "ssh_info": ssh_info,
                            "status": "creating",
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        }

        except Exception as e:
            logger.log_error("Fehler beim Erstellen der Vast.ai Instanz", error=e)
            raise

    async def _wait_for_ssh(
        self, instance_id: str, max_retries: int = 30
    ) -> Dict[str, Any]:
        """
        Wartet auf SSH-Verfügbarkeit der Instanz.
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_config['vast_ai']['api_key']}"
                }
                ssh_url = f"{self.api_config['vast_ai']['base_url']}{self.api_config['vast_ai']['endpoints']['ssh']}"
                ssh_url = ssh_url.format(instance_id=instance_id)

                for _ in range(max_retries):
                    async with session.get(ssh_url, headers=headers) as response:
                        if response.status == 200:
                            ssh_data = await response.json()
                            return {
                                "host": ssh_data["ssh_host"],
                                "port": ssh_data["ssh_port"],
                                "username": self.ssh_config["username"],
                                "key_path": self.ssh_config["key_path"],
                            }

                    await asyncio.sleep(10)  # Warte 10 Sekunden zwischen Versuchen

                raise Exception("Timeout beim Warten auf SSH-Verfügbarkeit")

        except Exception as e:
            logger.log_error("Fehler beim Warten auf SSH-Verfügbarkeit", error=e)
            raise

    async def _destroy_vast_instance(self, instance_id: str) -> bool:
        """
        Beendet eine Vast.ai Instanz.
        """
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_config['vast_ai']['api_key']}"
                }
                destroy_url = f"{self.api_config['vast_ai']['base_url']}{self.api_config['vast_ai']['endpoints']['destroy']}"
                destroy_url = destroy_url.format(instance_id=instance_id)

                async with session.post(destroy_url, headers=headers) as response:
                    if response.status != 200:
                        raise Exception(
                            f"Fehler beim Beenden der Instanz: {response.status}"
                        )

                    return True

        except Exception as e:
            logger.log_error("Fehler beim Beenden der Vast.ai Instanz", error=e)
            return False

    async def _scale_up(self) -> Dict[str, Any]:
        """Skaliert die Anzahl der Instanzen nach oben."""
        try:
            if len(self.active_instances) >= self.max_instances:
                return {
                    "action": "maintain",
                    "reason": "Maximale Instanzanzahl erreicht",
                }

            # Bestimme beste Instanzkonfiguration
            instance_config = await self.get_optimal_instance_config(
                processing_time=1.0,  # Basis-Zeit
                required_models=["clip", "whisper"],
                current_load=self._calculate_current_load(),
            )

            # Erstelle neue Instanz
            new_instance = await self._create_vast_instance(
                instance_config["instance_type"]
            )

            # Füge zur aktiven Instanzen hinzu
            self.active_instances[new_instance["instance_id"]] = {
                "config": instance_config,
                "status": new_instance["status"],
                "ssh_info": new_instance["ssh_info"],
                "created_at": new_instance["created_at"],
                "current_load": 0.0,
            }

            return {
                "action": "scale_up",
                "new_instance": new_instance,
                "new_instance_count": len(self.active_instances),
            }

        except Exception as e:
            logger.log_error("Fehler beim Hochskalieren", error=e)
            raise

    async def _scale_down(self) -> Dict[str, Any]:
        """Skaliert die Anzahl der Instanzen nach unten."""
        try:
            if len(self.active_instances) <= 1:
                return {
                    "action": "maintain",
                    "reason": "Minimale Instanzanzahl erreicht",
                }

            # Finde am wenigsten ausgelastete Instanz
            least_loaded = min(
                self.active_instances.items(), key=lambda x: x[1]["current_load"]
            )

            instance_id, instance_data = least_loaded

            # Beende Instanz
            if await self._destroy_vast_instance(instance_id):
                # Entferne aus aktiven Instanzen
                del self.active_instances[instance_id]

                return {
                    "action": "scale_down",
                    "removed_instance": instance_id,
                    "new_instance_count": len(self.active_instances),
                }
            else:
                return {
                    "action": "maintain",
                    "reason": "Fehler beim Beenden der Instanz",
                }

        except Exception as e:
            logger.log_error("Fehler beim Runterskalieren", error=e)
            raise

    async def update_instance_status(self) -> None:
        """
        Aktualisiert den Status aller aktiven Instanzen.
        """
        try:
            for instance_id, instance_data in self.active_instances.items():
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {self.api_config['vast_ai']['api_key']}"
                    }
                    status_url = f"{self.api_config['vast_ai']['base_url']}{self.api_config['vast_ai']['endpoints']['status']}"
                    status_url = status_url.format(instance_id=instance_id)

                    async with session.get(status_url, headers=headers) as response:
                        if response.status == 200:
                            status_data = await response.json()
                            instance_data["status"] = status_data["status"]

                            # Aktualisiere Last basierend auf GPU-Auslastung
                            if "gpu_utilization" in status_data:
                                instance_data["current_load"] = (
                                    float(status_data["gpu_utilization"]) / 100.0
                                )

        except Exception as e:
            logger.log_error("Fehler beim Aktualisieren der Instanz-Status", error=e)

    def _calculate_current_load(self) -> float:
        """Berechnet die aktuelle Last der Instanzen."""
        try:
            if not self.active_instances:
                return 0.0

            total_load = sum(
                instance["current_load"] for instance in self.active_instances.values()
            )

            return total_load / len(self.active_instances)

        except Exception as e:
            logger.log_error("Fehler bei der Lastberechnung", error=e)
            return 0.0


class RestraintDetector:
    def __init__(self):
        """Initialisiert den Restraint Detector mit CLIP-Modell und Whisper."""
        try:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            # Vision Model
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(
                self.device
            )
            self.processor = CLIPProcessor.from_pretrained(
                "openai/clip-vit-base-patch32"
            )

            # Audio Model
            self.whisper_processor = WhisperProcessor.from_pretrained(
                "openai/whisper-base"
            )
            self.whisper_model = WhisperForConditionalGeneration.from_pretrained(
                "openai/whisper-base"
            ).to(self.device)

            # Performance-Optimierungen
            self.batch_size = 32  # Optimale Batch-Größe für GPU
            self.gpu_memory_threshold = 0.8  # GPU-Speicher-Schwellenwert
            self.cache_ttl = 3600  # Cache-TTL in Sekunden
            self.frame_sampling_rate = 2  # Jedes n-te Frame wird analysiert
            self.max_workers = 4  # Maximale Anzahl paralleler Worker

            # CUDA-Optimierungen
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True

            # Redis für Caching
            self.redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "redis"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                db=int(os.getenv("REDIS_DB", 0)),
            )

            # Thread-Pool für parallele Verarbeitung
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)

            # Cache für Frame-Hashes
            self._frame_cache = lru_cache(maxsize=1000)(self._analyze_frame_internal)

            # Audio-Analyse-Parameter
            self.audio_threshold = 0.7  # Schwellenwert für laute Geräusche
            self.silence_threshold = 0.1  # Schwellenwert für Stille
            self.min_silence_duration = 2.0  # Minimale Stille-Dauer in Sekunden

            # Kategorien für Fesselungen und Materialien
            self.categories = [
                # Grundlegende Fesselungsarten
                "rope restraint",
                "handcuffs",
                "leather restraints",
                "tape restraint",
                "rope",
                "leather",
                "metal chains",
                "plastic wrap",
                "tape",
                "restraints",
                "cuffs",
                "gags",
                "blindfolds",
                "collars",
                # BDSM-spezifische Materialien
                "shibari rope",
                "jute rope",
                "hemp rope",
                "nylon rope",
                "cotton rope",
                "leather cuffs",
                "leather collar",
                "leather harness",
                "leather straps",
                "metal cuffs",
                "metal collar",
                "metal chains",
                "metal rings",
                "rope bondage",
                "rope harness",
                "rope suspension",
                # Shibari-Techniken und Knoten
                "shibari pattern",
                "kinbaku",
                "rope knot",
                "rope tie",
                "diamond pattern",
                "karada",
                "takate kote",
                "ebi",
                "tsuri",
                "suspension",
                "partial suspension",
                # BDSM-Ausrüstung
                "spreader bar",
                "restraint system",
                "bondage furniture",
                "suspension frame",
                "bondage bed",
                "bondage chair",
                "wrist cuffs",
                "ankle cuffs",
                "thigh cuffs",
                "nipple clamps",
                "clamps",
                "restraint straps",
                # Materialien und Texturen
                "rough rope",
                "smooth rope",
                "waxed rope",
                "treated rope",
                "soft leather",
                "hard leather",
                "studded leather",
                "metal chain",
                "metal ring",
                "metal hook",
                "synthetic rope",
                "natural fiber rope",
                # Sicherheitsausrüstung
                "safety scissors",
                "rope cutter",
                "safety release",
                "emergency release",
                "quick release",
                "safety equipment",
                # Fesselungsart und Kontext
                "self bondage",
                "partner bondage",
                "solo bondage",
                "suspension bondage",
                "partial suspension",
                "ground bondage",
                "escape proof",
                "escape possible",
                "safety risk",
                # Anatomische und physische Faktoren
                "wrist position",
                "ankle position",
                "neck position",
                "body tension",
                "muscle strain",
                "circulation risk",
                "breathing restriction",
                "pressure points",
                # Verfügbare Hilfsmittel
                "safety tools nearby",
                "no safety tools",
                "emergency phone",
                "ice release",
                "timer release",
                "magnetic release",
                # Emotionale und mentale Faktoren
                "distressed person",
                "calm person",
                "panicked person",
                "experienced person",
                "inexperienced person",
                "safeword available",
                "no safeword",
                "communication possible",
                # Sicherheitsrisiken
                "high risk",
                "medium risk",
                "low risk",
                "unsafe position",
                "safe position",
                "circulation check",
                "breathing check",
                "pressure check",
                "temperature check",
                # Befreiungsmöglichkeiten
                "self release possible",
                "self release impossible",
                "partner release needed",
                "emergency release needed",
                "time based release",
                "condition based release",
                # Fesselungskontext und Zustimmung
                "consensual bondage",
                "non-consensual bondage",
                "forced restraint",
                "voluntary submission",
                "involuntary submission",
                "coerced submission",
                "resistance",
                "struggle",
                "compliance",
                "cooperation",
                "active participation",
                "passive submission",
                "forced position",
                # Körperliche und emotionale Anzeichen
                "physical resistance",
                "verbal resistance",
                "emotional distress",
                "fear",
                "anxiety",
                "panic",
                "calm acceptance",
                "muscle tension",
                "body language",
                "facial expression",
                "tears",
                "sweating",
                "rapid breathing",
                "hyperventilation",
                # Zwangsmittel und Überwältigung
                "weapon present",
                "threat",
                "intimidation",
                "physical force",
                "overpowering",
                "restraint marks",
                "struggle marks",
                "defensive wounds",
                "escape attempts",
                # Einvernehmliche Zeichen
                "safeword established",
                "aftercare available",
                "trust present",
                "communication",
                "negotiation",
                "consent check",
                "comfort check",
                "boundary respect",
                "scene negotiation",
                # Notfallindikatoren
                "immediate danger",
                "medical emergency",
                "psychological crisis",
                "trauma response",
                "dissociation",
                "freeze response",
                "fight response",
                "flight response",
                "fawn response",
                # Alleinlassensituationen
                "abandoned person",
                "left alone",
                "unattended person",
                "no supervision",
                "no assistance nearby",
                "isolated location",
                "remote area",
                "locked room",
                "soundproof room",
                "no escape route",
                "trapped situation",
                "time limit exceeded",
                # Überwachungs- und Sicherheitsaspekte
                "supervision present",
                "spotter available",
                "assistant nearby",
                "monitoring system",
                "camera present",
                "baby monitor",
                "intercom system",
                "emergency button",
                "panic button",
                # Zeitliche Faktoren
                "extended duration",
                "time limit",
                "timer present",
                "delayed release",
                "scheduled check",
                "regular monitoring",
                "check-in system",
                # Umgebungsfaktoren
                "safe environment",
                "unsafe environment",
                "hazardous conditions",
                "temperature risk",
                "ventilation risk",
                "fire hazard",
                "flood risk",
                "structural risk",
                "environmental danger",
                # Kommunikationsmöglichkeiten
                "communication device",
                "phone nearby",
                "walkie talkie",
                "signal system",
                "visual signal",
                "audible signal",
                "emergency contact",
                "neighbor alert",
                "community watch",
            ]

            # Sicherheitsregeln und Risikobewertung
            self.safety_rules = {
                "high_risk_factors": [
                    "suspension without spotter",
                    "no safety tools",
                    "breathing restriction",
                    "neck pressure",
                    "circulation risk",
                    "distressed person",
                    "inexperienced person",
                    "no safeword",
                    "no communication",
                    "non-consensual bondage",
                    "forced restraint",
                    "physical resistance",
                    "weapon present",
                    "threat",
                    "intimidation",
                    "immediate danger",
                    "medical emergency",
                    "psychological crisis",
                    "trauma response",
                    "abandoned person",
                    "left alone",
                    "unattended person",
                    "no supervision",
                    "no assistance nearby",
                    "isolated location",
                    "locked room",
                    "soundproof room",
                    "no escape route",
                    "trapped situation",
                    "time limit exceeded",
                    "unsafe environment",
                    "hazardous conditions",
                    "temperature risk",
                    "ventilation risk",
                    "fire hazard",
                ],
                "medium_risk_factors": [
                    "partial suspension",
                    "limited safety tools",
                    "some pressure points",
                    "moderate tension",
                    "limited communication",
                    "emotional distress",
                    "anxiety",
                    "panic",
                    "struggle marks",
                    "escape attempts",
                    "dissociation",
                    "remote area",
                    "extended duration",
                    "delayed release",
                    "limited supervision",
                    "partial monitoring",
                    "intermittent checks",
                ],
                "low_risk_factors": [
                    "ground bondage",
                    "safety tools available",
                    "good circulation",
                    "clear communication",
                    "experienced person",
                    "safeword established",
                    "aftercare available",
                    "trust present",
                    "communication",
                    "negotiation",
                    "supervision present",
                    "spotter available",
                    "assistant nearby",
                    "monitoring system",
                    "camera present",
                    "regular monitoring",
                    "check-in system",
                    "safe environment",
                    "communication device",
                    "emergency contact",
                ],
            }

            # Text-Embeddings für die Kategorien vorberechnen
            self.category_embeddings = self._prepare_category_embeddings()

            # Audio-bezogene Kategorien
            self.audio_categories = [
                # Notfallgeräusche
                "screaming",
                "crying",
                "shouting",
                "help",
                "emergency",
                "distress",
                "panic",
                "fear",
                "pain",
                "struggle",
                "banging",
                "knocking",
                "breaking",
                "crashing",
                # Kommunikationsgeräusche
                "talking",
                "negotiation",
                "safeword",
                "consent",
                "check-in",
                "communication",
                "discussion",
                # Umgebungsgeräusche
                "silence",
                "background noise",
                "music",
                "tv",
                "footsteps",
                "door",
                "window",
                "ventilation",
                # Emotionale Geräusche
                "laughing",
                "moaning",
                "breathing",
                "sighing",
                "whimpering",
                "sobbing",
                "hyperventilation",
            ]

            # GPU-Kosten-Konfiguration
            self.gpu_costs = {
                "USD": {
                    "hourly": 0.90,  # Kosten pro Stunde in USD
                    "minute": 0.015,  # Kosten pro Minute in USD
                    "second": 0.00025,  # Kosten pro Sekunde in USD
                },
                "EUR": {
                    "hourly": 0.82,  # Kosten pro Stunde in EUR
                    "minute": 0.014,  # Kosten pro Minute in EUR
                    "second": 0.00023,  # Kosten pro Sekunde in EUR
                },
            }

            # Geschätzte Verarbeitungszeiten pro Frame/Audio
            self.processing_times = {
                "frame_analysis": 0.15,  # Sekunden pro Frame
                "audio_analysis": 0.25,  # Sekunden pro Audio-Segment
                "batch_overhead": 0.05,  # Sekunden Overhead pro Batch
            }

            # Instanz-Manager initialisieren
            self.instance_manager = InstanceManager()

            logger.log_info(
                "Restraint Detector initialisiert",
                extra={"device": self.device, "categories": self.categories},
            )
        except Exception as e:
            logger.log_error(
                "Fehler bei der Initialisierung des Restraint Detectors", error=e
            )
            raise

    def _prepare_category_embeddings(self) -> torch.Tensor:
        """Bereitet die Text-Embeddings für die Kategorien vor."""
        try:
            inputs = self.processor(
                text=self.categories, return_tensors="pt", padding=True
            ).to(self.device)

            with torch.no_grad():
                text_features = self.model.get_text_features(**inputs)
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            return text_features
        except Exception as e:
            logger.log_error(
                "Fehler beim Vorbereiten der Kategorie-Embeddings", error=e
            )
            raise

    def _adjust_batch_size(self):
        """Passt die Batch-Größe basierend auf GPU-Speicher an."""
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated()
            memory_reserved = torch.cuda.memory_reserved()
            total_memory = torch.cuda.get_device_properties(0).total_memory

            memory_usage = (memory_allocated + memory_reserved) / total_memory

            if memory_usage > self.gpu_memory_threshold:
                self.batch_size = max(1, self.batch_size // 2)
                logger.log_warning(
                    "Batch-Größe reduziert",
                    extra={
                        "new_batch_size": self.batch_size,
                        "memory_usage": memory_usage,
                    },
                )
            elif memory_usage < self.gpu_memory_threshold * 0.5:
                self.batch_size = min(32, self.batch_size * 2)
                logger.log_info(
                    "Batch-Größe erhöht",
                    extra={
                        "new_batch_size": self.batch_size,
                        "memory_usage": memory_usage,
                    },
                )

    def _cleanup_gpu_memory(self):
        """Bereinigt GPU-Speicher."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()

    async def analyze_audio(
        self, audio_data: np.ndarray, sample_rate: int
    ) -> Dict[str, Any]:
        """
        Analysiert Audiodaten auf Notfallsituationen und Kommunikationsmuster.

        Args:
            audio_data: Audiodaten als numpy array
            sample_rate: Abtastrate der Audiodaten

        Returns:
            Dictionary mit den Audioanalyseergebnissen
        """
        try:
            # Audio-Features extrahieren
            mfcc = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data, sr=sample_rate
            )
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data, sr=sample_rate
            )

            # Lautstärke und Stille analysieren
            rms = librosa.feature.rms(y=audio_data)
            is_loud = np.mean(rms) > self.audio_threshold
            is_silent = np.mean(rms) < self.silence_threshold

            # Stille-Perioden erkennen
            silent_regions = librosa.effects.split(audio_data, top_db=20)
            long_silence = any(
                (end - start) / sample_rate > self.min_silence_duration
                for start, end in silent_regions
            )

            # Whisper Transkription
            input_features = self.whisper_processor(
                audio_data, sampling_rate=sample_rate, return_tensors="pt"
            ).input_features.to(self.device)

            with torch.no_grad():
                predicted_ids = self.whisper_model.generate(input_features)
                transcription = self.whisper_processor.batch_decode(
                    predicted_ids, skip_special_tokens=True
                )[0]

            # Notfallwörter erkennen
            emergency_words = ["help", "stop", "emergency", "danger", "pain"]
            has_emergency_words = any(
                word in transcription.lower() for word in emergency_words
            )

            # Safeword erkennen
            safewords = ["red", "safeword", "stop", "yellow"]
            has_safeword = any(word in transcription.lower() for word in safewords)

            # Emotionale Analyse
            emotional_indicators = {
                "distress": any(
                    word in transcription.lower()
                    for word in ["help", "stop", "pain", "scared", "afraid"]
                ),
                "consent": any(
                    word in transcription.lower()
                    for word in ["yes", "okay", "continue", "good"]
                ),
                "communication": len(transcription.split()) > 5,
            }

            return {
                "audio_analysis": {
                    "is_loud": bool(is_loud),
                    "is_silent": bool(is_silent),
                    "has_long_silence": bool(long_silence),
                    "transcription": transcription,
                    "has_emergency_words": has_emergency_words,
                    "has_safeword": has_safeword,
                    "emotional_indicators": emotional_indicators,
                    "audio_features": {
                        "mfcc_mean": float(np.mean(mfcc)),
                        "spectral_centroid_mean": float(np.mean(spectral_centroid)),
                        "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
                    },
                }
            }

        except Exception as e:
            logger.log_error("Fehler bei der Audio-Analyse", error=e)
            raise

    def _estimate_processing_time(
        self, frame_count: int, audio_duration: Optional[float] = None
    ) -> float:
        """
        Schätzt die benötigte Verarbeitungszeit basierend auf den Medienmerkmalen.

        Args:
            frame_count: Anzahl der zu verarbeitenden Frames
            audio_duration: Dauer der Audiodaten in Sekunden (optional)

        Returns:
            Geschätzte Verarbeitungszeit in Sekunden
        """
        try:
            # Basis-Zeit für Frame-Analyse
            total_time = frame_count * self.processing_times["frame_analysis"]

            # Audio-Analyse-Zeit hinzufügen wenn vorhanden
            if audio_duration is not None:
                audio_segments = math.ceil(
                    audio_duration / 30
                )  # 30 Sekunden pro Segment
                total_time += audio_segments * self.processing_times["audio_analysis"]

            # Batch-Overhead hinzufügen
            batch_count = math.ceil(frame_count / self.batch_size)
            total_time += batch_count * self.processing_times["batch_overhead"]

            return total_time

        except Exception as e:
            logger.log_error("Fehler bei der Verarbeitungszeit-Schätzung", error=e)
            raise

    def _calculate_gpu_cost(
        self, processing_time: float, currency: str = "EUR"
    ) -> Dict[str, float]:
        """
        Berechnet die GPU-Kosten basierend auf der Verarbeitungszeit.

        Args:
            processing_time: Verarbeitungszeit in Sekunden
            currency: Währung (USD oder EUR)

        Returns:
            Dictionary mit Kosten in verschiedenen Zeiteinheiten
        """
        try:
            if currency not in self.gpu_costs:
                currency = "EUR"  # Fallback auf EUR

            costs = self.gpu_costs[currency]

            return {
                "seconds": round(processing_time * costs["second"], 4),
                "minutes": round(processing_time / 60 * costs["minute"], 4),
                "hours": round(processing_time / 3600 * costs["hourly"], 4),
                "currency": currency,
            }

        except Exception as e:
            logger.log_error("Fehler bei der GPU-Kostenberechnung", error=e)
            raise

    async def _get_instance_costs(self, processing_time: float) -> Dict[str, Any]:
        """Holt aktuelle Instanzkosten und berechnet Preis/Leistungsverhältnis."""
        try:
            prices = await self.instance_manager.instance_provider.fetch_prices()
            price_performance = (
                self.instance_manager.instance_provider.calculate_price_performance(
                    prices, processing_time
                )
            )

            return {
                "available_instances": price_performance,
                "recommended_instance": (
                    price_performance[0] if price_performance else None
                ),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.log_error("Fehler beim Abrufen der Instanzkosten", error=e)
            return {}

    async def analyze_frame(
        self,
        image: Union[str, np.ndarray, Image.Image],
        confidence_threshold: float = 0.7,
        detection_mode: str = "comprehensive",
    ) -> Dict[str, Any]:
        """
        Analysiert einen Frame auf Restraint-Erkennungen mit Pipeline-Architektur.

        Args:
            image: Bilddaten in verschiedenen Formaten
            confidence_threshold: Mindest-Konfidenz für Erkennungen
            detection_mode: Erkennungsmodus (comprehensive, fast, detailed)

        Returns:
            Analyse-Ergebnisse mit Erkennungen und Metadaten
        """
        try:
            # Pipeline-Phase 1: Bild-Preprocessing
            processed_image = await self._preprocess_image(image)

            # Pipeline-Phase 2: Erkennung basierend auf Modus
            detections = await self._detect_restraints_by_mode(
                processed_image, detection_mode, confidence_threshold
            )

            # Pipeline-Phase 3: Post-Processing und Validierung
            validated_detections = await self._validate_and_enhance_detections(
                detections, processed_image
            )

            # Pipeline-Phase 4: Ergebnis-Assemblierung
            return await self._assemble_analysis_result(
                validated_detections, processed_image, confidence_threshold
            )

        except Exception as e:
            logger.log_error(f"Fehler bei Frame-Analyse: {str(e)}", error=e)
            return self._create_error_result(str(e))

    async def _preprocess_image(self, image: Union[str, np.ndarray, Image.Image]) -> np.ndarray:
        """Pipeline-Phase 1: Standardisiert und bereitet Bild vor."""
        # Format-Konvertierung
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"Konnte Bild nicht laden: {image}")
        elif isinstance(image, Image.Image):
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            img = image.copy()

        # Basis-Validierung
        if img.size == 0:
            raise ValueError("Leeres Bild erhalten")

        # Größen-Normalisierung für bessere Performance
        height, width = img.shape[:2]
        if max(height, width) > 1024:
            scale = 1024 / max(height, width)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))

        return img

    async def _detect_restraints_by_mode(
        self,
        image: np.ndarray,
        mode: str,
        threshold: float
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Pipeline-Phase 2: Erkennung nach gewähltem Modus."""
        if mode == "fast":
            return await self._fast_detection(image, threshold)
        elif mode == "detailed":
            return await self._detailed_detection(image, threshold)
        else:  # comprehensive (default)
            return await self._comprehensive_detection(image, threshold)

    async def _fast_detection(self, image: np.ndarray, threshold: float) -> Dict[str, List[Dict[str, Any]]]:
        """Schnelle Erkennung für Real-time Anwendungen."""
        results = {
            "restraints": [],
            "body_parts": [],
            "poses": []
        }

        # Nur grundlegende Objekt-Erkennung
        restraints = await self._detect_restraint_objects(image, threshold)
        results["restraints"] = restraints

        return results

    async def _detailed_detection(self, image: np.ndarray, threshold: float) -> Dict[str, List[Dict[str, Any]]]:
        """Detaillierte Analyse mit erweiterten Features."""
        # Parallel-Verarbeitung aller Erkennungstypen
        tasks = [
            self._detect_restraint_objects(image, threshold),
            self._detect_body_parts(image, threshold),
            self._detect_poses(image, threshold),
            self._detect_interactions(image, threshold),
            self._detect_materials(image, threshold)
        ]

        restraints, body_parts, poses, interactions, materials = await asyncio.gather(*tasks)

        return {
            "restraints": restraints,
            "body_parts": body_parts,
            "poses": poses,
            "interactions": interactions,
            "materials": materials
        }

    async def _comprehensive_detection(self, image: np.ndarray, threshold: float) -> Dict[str, List[Dict[str, Any]]]:
        """Umfassende Analyse mit allen verfügbaren Methoden."""
        # Basis-Erkennungen
        base_results = await self._detailed_detection(image, threshold)

        # Erweiterte Analysen
        extended_tasks = [
            self._detect_scene_context(image, threshold),
            self._detect_emotional_states(image, threshold),
            self._analyze_lighting_shadows(image),
            self._detect_environmental_factors(image)
        ]

        scene_context, emotions, lighting, environment = await asyncio.gather(*extended_tasks)

        # Zusammenführung
        base_results.update({
            "scene_context": scene_context,
            "emotions": emotions,
            "lighting": lighting,
            "environment": environment
        })

        return base_results

    async def _validate_and_enhance_detections(
        self,
        detections: Dict[str, List[Dict[str, Any]]],
        image: np.ndarray
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Pipeline-Phase 3: Validierung und Verbesserung der Erkennungen."""
        validated = {}

        for category, items in detections.items():
            validated[category] = []

            for item in items:
                # Konfidenz-Validierung
                if self._validate_detection_confidence(item):
                    # Spatial-Validierung
                    if self._validate_spatial_consistency(item, image):
                        # Kontext-Validierung
                        enhanced_item = await self._enhance_detection_context(item, detections)
                        validated[category].append(enhanced_item)

        return validated

    def _validate_detection_confidence(self, detection: Dict[str, Any]) -> bool:
        """Validiert Erkennungs-Konfidenz."""
        confidence = detection.get("confidence", 0)
        detection_type = detection.get("type", "unknown")

        # Typ-spezifische Schwellwerte
        type_thresholds = {
            "restraint": 0.6,
            "rope": 0.7,
            "chain": 0.8,
            "body_part": 0.5,
            "pose": 0.6
        }

        threshold = type_thresholds.get(detection_type, 0.7)
        return confidence >= threshold

    def _validate_spatial_consistency(self, detection: Dict[str, Any], image: np.ndarray) -> bool:
        """Validiert räumliche Konsistenz der Erkennung."""
        bbox = detection.get("bbox", [])
        if len(bbox) != 4:
            return False

        x, y, w, h = bbox
        img_height, img_width = image.shape[:2]

        # Boundary-Checks
        if x < 0 or y < 0 or x + w > img_width or y + h > img_height:
            return False

        # Size-Plausibilität
        area = w * h
        img_area = img_width * img_height
        area_ratio = area / img_area

        return 0.001 <= area_ratio <= 0.8  # Zwischen 0.1% und 80% des Bildes

    async def _enhance_detection_context(
        self,
        detection: Dict[str, Any],
        all_detections: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Erweitert Erkennung um Kontext-Informationen."""
        enhanced = detection.copy()

        # Nachbar-Analysen
        enhanced["neighbors"] = self._find_neighboring_detections(detection, all_detections)

        # Interaktions-Score
        enhanced["interaction_score"] = self._calculate_interaction_score(detection, all_detections)

        # Relevanz-Score basierend auf Kontext
        enhanced["relevance_score"] = self._calculate_relevance_score(enhanced)

        return enhanced

    def _find_neighboring_detections(
        self,
        target: Dict[str, Any],
        all_detections: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Findet benachbarte Erkennungen."""
        neighbors = []
        target_bbox = target.get("bbox", [])

        if len(target_bbox) != 4:
            return neighbors

        for category, detections in all_detections.items():
            for detection in detections:
                if detection == target:
                    continue

                if self._calculate_proximity(target_bbox, detection.get("bbox", [])) < 100:
                    neighbors.append({
                        "type": detection.get("type"),
                        "confidence": detection.get("confidence"),
                        "distance": self._calculate_proximity(target_bbox, detection.get("bbox", []))
                    })

        return sorted(neighbors, key=lambda x: x["distance"])[:5]  # Top 5

    def _calculate_proximity(self, bbox1: List[float], bbox2: List[float]) -> float:
        """Berechnet Entfernung zwischen zwei Bounding Boxes."""
        if len(bbox1) != 4 or len(bbox2) != 4:
            return float('inf')

        # Zentren der Boxen
        x1_center = bbox1[0] + bbox1[2] / 2
        y1_center = bbox1[1] + bbox1[3] / 2
        x2_center = bbox2[0] + bbox2[2] / 2
        y2_center = bbox2[1] + bbox2[3] / 2

        # Euklidische Distanz
        return math.sqrt((x1_center - x2_center) ** 2 + (y1_center - y2_center) ** 2)

    def _calculate_interaction_score(
        self,
        detection: Dict[str, Any],
        all_detections: Dict[str, List[Dict[str, Any]]]
    ) -> float:
        """Berechnet Interaktions-Score basierend auf Kontext."""
        score = 0.0

        # Base-Score von Konfidenz
        score += detection.get("confidence", 0) * 0.4

        # Nachbar-Bonus
        neighbors = self._find_neighboring_detections(detection, all_detections)
        neighbor_bonus = min(len(neighbors) * 0.1, 0.3)
        score += neighbor_bonus

        # Typ-spezifische Boni
        detection_type = detection.get("type", "")
        if detection_type in ["restraint", "rope", "chain"]:
            score += 0.2

        return min(score, 1.0)

    def _calculate_relevance_score(self, detection: Dict[str, Any]) -> float:
        """Berechnet Relevanz-Score für Priorisierung."""
        relevance = detection.get("confidence", 0) * 0.5
        relevance += detection.get("interaction_score", 0) * 0.3
        relevance += len(detection.get("neighbors", [])) * 0.02

        return min(relevance, 1.0)

    async def _assemble_analysis_result(
        self,
        detections: Dict[str, List[Dict[str, Any]]],
        image: np.ndarray,
        confidence_threshold: float
    ) -> Dict[str, Any]:
        """Pipeline-Phase 4: Assembliert finale Analyse-Ergebnisse."""
        total_detections = sum(len(items) for items in detections.values())

        # Top-Erkennungen nach Relevanz
        top_detections = self._get_top_detections(detections, limit=10)

        # Gesamt-Konfidenz berechnen
        overall_confidence = self._calculate_overall_confidence(detections)

        # Risk-Assessment
        risk_level = self._assess_risk_level(detections, overall_confidence)

        return {
            "success": True,
            "total_detections": total_detections,
            "detections": detections,
            "top_detections": top_detections,
            "overall_confidence": overall_confidence,
            "risk_level": risk_level,
            "image_dimensions": image.shape[:2],
            "confidence_threshold": confidence_threshold,
            "processing_timestamp": datetime.now().isoformat()
        }

    def _get_top_detections(self, detections: Dict[str, List[Dict[str, Any]]], limit: int = 10) -> List[Dict[str, Any]]:
        """Ermittelt Top-Erkennungen nach Relevanz."""
        all_items = []
        for category, items in detections.items():
            for item in items:
                item_copy = item.copy()
                item_copy["category"] = category
                all_items.append(item_copy)

        # Sortierung nach Relevanz-Score
        sorted_items = sorted(all_items, key=lambda x: x.get("relevance_score", 0), reverse=True)
        return sorted_items[:limit]

    def _calculate_overall_confidence(self, detections: Dict[str, List[Dict[str, Any]]]) -> float:
        """Berechnet Gesamt-Konfidenz der Analyse."""
        all_confidences = []
        for items in detections.values():
            for item in items:
                confidence = item.get("confidence", 0)
                if confidence > 0:
                    all_confidences.append(confidence)

        if not all_confidences:
            return 0.0

        # Weighted average mit Top-Erkennungen
        all_confidences.sort(reverse=True)
            # Frame-Hashing für Caching
            frame_hash = self._compute_frame_hash(frame)

            # Cache prüfen
            cache_key = f"frame:{frame_hash}"
            cached_result = self.redis_client.get(cache_key)
            if cached_result:
                return pickle.loads(cached_result)

            # Frame vorbereiten
            image = self.processor(images=frame, return_tensors="pt").to(self.device)

            # Batch-Größe anpassen
            self._adjust_batch_size()

            # Bild-Embedding berechnen
            with torch.no_grad():
                image_features = self.model.get_image_features(**image)
                image_features = image_features / image_features.norm(
                    dim=-1, keepdim=True
                )

            # Ähnlichkeiten berechnen
            similarity = (100.0 * image_features @ self.category_embeddings.T).softmax(
                dim=-1
            )

            # Ergebnisse formatieren
            results = []
            risk_factors = []
            consent_assessment = {
                "consent_level": "unknown",
                "risk_level": "unknown",
                "consent_indicators": [],
                "non_consent_indicators": [],
                "safety_concerns": [],
                "recommendations": [],
                "emergency_intervention_needed": False,
            }

            supervision_assessment = {
                "supervision_status": "unknown",
                "abandonment_risk": "unknown",
                "supervision_indicators": [],
                "abandonment_indicators": [],
                "environmental_risks": [],
                "communication_options": [],
                "safety_concerns": [],
                "recommendations": [],
                "emergency_intervention_needed": False,
            }

            # Asynchrone Audio-Analyse wenn verfügbar
            audio_analysis = None
            if audio_data is not None and sample_rate is not None:
                audio_analysis = await self.analyze_audio(audio_data, sample_rate)

            # Ergebnisse verarbeiten
            for idx, (category, score) in enumerate(
                zip(self.categories, similarity[0])
            ):
                if score > 0.1:  # Nur relevante Ergebnisse
                    results.append({"category": category, "confidence": float(score)})

                    # Risikofaktoren sammeln
                    if category in self.safety_rules["high_risk_factors"]:
                        risk_factors.append(("high", category))
                    elif category in self.safety_rules["medium_risk_factors"]:
                        risk_factors.append(("medium", category))
                    elif category in self.safety_rules["low_risk_factors"]:
                        risk_factors.append(("low", category))

                    # Zustimmungsindikatoren sammeln
                    if any(
                        indicator in category
                        for indicator in [
                            "consensual",
                            "voluntary",
                            "safeword",
                            "aftercare",
                            "trust",
                            "communication",
                            "negotiation",
                            "cooperation",
                        ]
                    ):
                        consent_assessment["consent_indicators"].append(category)
                    elif any(
                        indicator in category
                        for indicator in [
                            "non-consensual",
                            "forced",
                            "resistance",
                            "struggle",
                            "threat",
                            "intimidation",
                            "weapon",
                            "coerced",
                        ]
                    ):
                        consent_assessment["non_consent_indicators"].append(category)

                    # Überwachungsindikatoren sammeln
                    if any(
                        indicator in category
                        for indicator in [
                            "supervision",
                            "spotter",
                            "assistant",
                            "monitoring",
                            "camera",
                            "regular",
                            "check-in",
                            "safe environment",
                        ]
                    ):
                        supervision_assessment["supervision_indicators"].append(
                            category
                        )
                    elif any(
                        indicator in category
                        for indicator in [
                            "abandoned",
                            "alone",
                            "unattended",
                            "no supervision",
                            "isolated",
                            "remote",
                            "locked",
                            "soundproof",
                        ]
                    ):
                        supervision_assessment["abandonment_indicators"].append(
                            category
                        )
                        supervision_assessment["emergency_intervention_needed"] = True

            # Audio-Ergebnisse einbeziehen
            if audio_analysis:
                if audio_analysis["audio_analysis"]["has_emergency_words"]:
                    consent_assessment["non_consent_indicators"].append(
                        "verbal emergency"
                    )
                    consent_assessment["emergency_intervention_needed"] = True

                if audio_analysis["audio_analysis"]["has_safeword"]:
                    consent_assessment["consent_indicators"].append("safeword used")

                if audio_analysis["audio_analysis"]["has_long_silence"]:
                    supervision_assessment["abandonment_indicators"].append(
                        "extended silence"
                    )
                    supervision_assessment["emergency_intervention_needed"] = True

                if audio_analysis["audio_analysis"]["is_loud"]:
                    supervision_assessment["safety_concerns"].append("unusual loudness")

            # Zustimmungsbewertung
            if consent_assessment["non_consent_indicators"]:
                consent_assessment["consent_level"] = "non-consensual"
                consent_assessment["emergency_intervention_needed"] = True
                consent_assessment["recommendations"].append(
                    "Sofortige Intervention erforderlich - Möglicher Zwang oder Überwältigung"
                )
            elif consent_assessment["consent_indicators"]:
                consent_assessment["consent_level"] = "consensual"

            # Überwachungsbewertung
            if supervision_assessment["abandonment_indicators"]:
                supervision_assessment["supervision_status"] = "abandoned"
                supervision_assessment["abandonment_risk"] = "high"
                supervision_assessment["recommendations"].append(
                    "Sofortige Intervention erforderlich - Person möglicherweise allein gelassen"
                )
            elif supervision_assessment["supervision_indicators"]:
                supervision_assessment["supervision_status"] = "supervised"
                supervision_assessment["abandonment_risk"] = "low"

            # Kostenberechnung
            audio_duration = (
                len(audio_data) / sample_rate if audio_data is not None else None
            )
            processing_time = self._estimate_processing_time(1, audio_duration)
            instance_costs = await self._get_instance_costs(processing_time)

            # Berechne optimale Instanzkonfiguration
            current_load = self._calculate_current_load()
            instance_config = await self.instance_manager.get_optimal_instance_config(
                processing_time,
                ["clip", "whisper"] if audio_data is not None else ["clip"],
                current_load,
            )

            # Ergebnisse cachen
            result = {
                "restraint_data": {
                    "detections": results,
                    "has_restraints": len(results) > 0,
                    "safety_assessment": consent_assessment,
                    "supervision_assessment": supervision_assessment,
                    "audio_analysis": audio_analysis,
                    "processing_info": {
                        "estimated_processing_time": round(processing_time, 2),
                        "instance_costs": instance_costs,
                    },
                    "instance_config": instance_config,
                }
            }

            self.redis_client.setex(cache_key, self.cache_ttl, pickle.dumps(result))

            # GPU-Speicher bereinigen
            self._cleanup_gpu_memory()

            return result

        except Exception as e:
            logger.log_error("Fehler bei der Frame-Analyse", error=e)
            raise

    def _calculate_current_load(self) -> float:
        """Berechnet die aktuelle Last der Instanzen."""
        try:
            if not self.instance_manager.active_instances:
                return 0.0

            total_load = sum(
                instance["current_load"]
                for instance in self.instance_manager.active_instances.values()
            )

            return total_load / len(self.instance_manager.active_instances)

        except Exception as e:
            logger.log_error("Fehler bei der Lastberechnung", error=e)
            return 0.0

    async def process_batch(
        self,
        frames: List[np.ndarray],
        audio_data: Optional[List[np.ndarray]] = None,
        sample_rates: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Verarbeitet einen Batch von Frames und optional Audiodaten.
        """
        try:
            # Frames in optimale Batch-Größe aufteilen
            batches = []
            current_batch = []

            for i, frame in enumerate(frames):
                current_batch.append(
                    (
                        frame,
                        audio_data[i] if audio_data else None,
                        sample_rates[i] if sample_rates else None,
                    )
                )

                if len(current_batch) >= self.batch_size:
                    batches.append(current_batch)
                    current_batch = []

            if current_batch:
                batches.append(current_batch)

            # Asynchrone Batch-Verarbeitung
            async with aiohttp.ClientSession():
                tasks = []
                for batch in batches:
                    for frame, audio, sample_rate in batch:
                        tasks.append(self.analyze_frame(frame, audio, sample_rate))

                results = await asyncio.gather(*tasks)

            # Kostenberechnung für den gesamten Batch
            total_audio_duration = (
                sum(len(audio) / rate for audio, rate in zip(audio_data, sample_rates))
                if audio_data
                else None
            )
            processing_time = self._estimate_processing_time(
                len(frames), total_audio_duration
            )
            instance_costs = await self._get_instance_costs(processing_time)

            # Batch-Ergebnisse erweitern
            batch_info = {
                "batch_processing_info": {
                    "frame_count": len(frames),
                    "estimated_processing_time": round(processing_time, 2),
                    "instance_costs": instance_costs,
                }
            }

            # Batch-Info zu jedem Ergebnis hinzufügen
            for result in results:
                result["restraint_data"].update(batch_info)

            return results

        except Exception as e:
            logger.log_error("Fehler bei der Batch-Verarbeitung", error=e)
            raise


# Detector-Instanz erstellen
detector = RestraintDetector()


class FrameRequest(BaseModel):
    """Request-Modell für die Frame-Analyse."""

    frame: List[int]  # Base64-kodiertes Bild
    audio_data: Optional[List[float]] = None  # Audiodaten
    sample_rate: Optional[int] = None  # Abtastrate


class BatchRequest(BaseModel):
    """Request-Modell für die Batch-Analyse."""

    frames: List[List[int]]  # Liste von Base64-kodierten Bildern


@app.post("/analyze/frame")
async def analyze_frame(request: FrameRequest) -> Dict[str, Any]:
    """
    Analysiert ein Frame und optional Audiodaten.
    """
    try:
        # Base64-Dekodierung
        frame = np.frombuffer(bytes(request.frame), dtype=np.uint8)
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Ungültiges Bildformat")

        # Audio-Daten verarbeiten wenn vorhanden
        audio_data = None
        if request.audio_data is not None and request.sample_rate is not None:
            audio_data = np.array(request.audio_data)

        result = await detector.analyze_frame(frame, audio_data, request.sample_rate)
        return result
    except Exception as e:
        logger.log_error("Fehler bei der Frame-Analyse", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/batch")
async def analyze_batch(request: BatchRequest) -> List[Dict[str, Any]]:
    """
    Analysiert einen Batch von Frames.

    Args:
        request: BatchRequest mit den zu analysierenden Bildern

    Returns:
        Liste von Analyseergebnissen
    """
    try:
        # Base64-Dekodierung
        frames = []
        for frame_data in request.frames:
            frame = np.frombuffer(bytes(frame_data), dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            if frame is None:
                raise HTTPException(status_code=400, detail="Ungültiges Bildformat")
            frames.append(frame)

        results = await detector.process_batch(frames)
        return results
    except Exception as e:
        logger.log_error("Fehler bei der Batch-Analyse", error=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health Check Endpoint."""
    return {"status": "healthy"}

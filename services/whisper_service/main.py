from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import whisper
import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Union
import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import soundfile as sf
from functools import lru_cache
from transformers import (
    Wav2Vec2ForSequenceClassification,
    Wav2Vec2FeatureExtractor,
    Wav2Vec2Model,
)
import torch.nn.functional as F
import librosa
import noisereduce as nr
from scipy import signal
from sklearn.metrics.pairwise import cosine_similarity
import faiss
import json
import os
from datetime import datetime
import requests
from PIL import Image
import base64

# Logger konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whisper_service")

app = FastAPI(
    title="Whisper Service",
    description="Service für GPU-basierte Spracherkennung, Emotionsanalyse und kombinierte Face-Voice-ID",
)


class PersonIdentifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.voice_id_service = VoiceIDService()
        self.face_id_service = FaceIDService()
        self.person_database = {}
        self.load_person_database()

    def load_person_database(self):
        """Lädt die Personendatenbank"""
        try:
            if os.path.exists("person_database.json"):
                with open("person_database.json", "r") as f:
                    self.person_database = json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Personendatenbank: {str(e)}")

    def save_person_database(self):
        """Speichert die Personendatenbank"""
        try:
            with open("person_database.json", "w") as f:
                json.dump(self.person_database, f)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Personendatenbank: {str(e)}")

    def register_person(
        self,
        voice_audio: np.ndarray,
        voice_sr: int,
        face_image: Optional[bytes] = None,
        metadata: Dict = None,
    ) -> str:
        """Registriert eine neue Person mit Stimme und/oder Gesicht"""
        try:
            person_id = f"person_{len(self.person_database)}"

            # Voice-ID registrieren
            voice_id = self.voice_id_service.register_voice(
                voice_audio, voice_sr, {"person_id": person_id, **metadata}
            )

            # Face-ID registrieren wenn vorhanden
            face_id = None
            if face_image is not None:
                face_id = self.face_id_service.register_face(
                    face_image, {"person_id": person_id, **metadata}
                )

            # Person in Datenbank speichern
            self.person_database[person_id] = {
                "voice_id": voice_id,
                "face_id": face_id,
                "metadata": metadata,
                "registered_at": datetime.now().isoformat(),
            }

            self.save_person_database()
            return person_id

        except Exception as e:
            logger.error(f"Fehler beim Registrieren der Person: {str(e)}")
            raise

    def identify_person(
        self,
        voice_audio: Optional[np.ndarray] = None,
        voice_sr: Optional[int] = None,
        face_image: Optional[bytes] = None,
        threshold: float = 0.8,
    ) -> List[Dict]:
        """Identifiziert eine Person anhand von Stimme und/oder Gesicht"""
        try:
            results = []

            # Voice-ID wenn vorhanden
            if voice_audio is not None and voice_sr is not None:
                voice_matches = self.voice_id_service.identify_voice(
                    voice_audio, voice_sr, threshold
                )
                for match in voice_matches:
                    person_id = match["person_id"]
                    if person_id in self.person_database:
                        results.append(
                            {
                                "person_id": person_id,
                                "voice_similarity": match["similarity"],
                                "face_similarity": None,
                                "metadata": self.person_database[person_id]["metadata"],
                            }
                        )

            # Face-ID wenn vorhanden
            if face_image is not None:
                face_matches = self.face_id_service.identify_face(face_image, threshold)
                for match in face_matches:
                    person_id = match["person_id"]
                    if person_id in self.person_database:
                        # Existierenden Eintrag aktualisieren oder neuen erstellen
                        existing_result = next(
                            (r for r in results if r["person_id"] == person_id), None
                        )
                        if existing_result:
                            existing_result["face_similarity"] = match["similarity"]
                        else:
                            results.append(
                                {
                                    "person_id": person_id,
                                    "voice_similarity": None,
                                    "face_similarity": match["similarity"],
                                    "metadata": self.person_database[person_id][
                                        "metadata"
                                    ],
                                }
                            )

            # Kombinierte Ähnlichkeit berechnen
            for result in results:
                similarities = [
                    s
                    for s in [result["voice_similarity"], result["face_similarity"]]
                    if s is not None
                ]
                if similarities:
                    result["combined_similarity"] = sum(similarities) / len(
                        similarities
                    )
                else:
                    result["combined_similarity"] = None

            # Nach kombinierter Ähnlichkeit sortieren
            results.sort(
                key=lambda x: (
                    x["combined_similarity"]
                    if x["combined_similarity"] is not None
                    else 0
                ),
                reverse=True,
            )

            return results

        except Exception as e:
            logger.error(f"Fehler bei der Personenidentifikation: {str(e)}")
            raise


class VoiceIDService:
    def __init__(self, model_path: str = "facebook/wav2vec2-base-960h"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = Wav2Vec2Model.from_pretrained(model_path).to(self.device)
        self.processor = Wav2Vec2FeatureExtractor.from_pretrained(model_path)
        self.model.eval()

        # FAISS Index für schnelle Ähnlichkeitssuche
        self.index = faiss.IndexFlatL2(768)  # 768 ist die Embedding-Dimension
        self.voice_embeddings = []
        self.voice_metadata = []

        # Lade gespeicherte Voice-IDs
        self.load_voice_ids()

    def load_voice_ids(self):
        """Lädt gespeicherte Voice-IDs"""
        try:
            if os.path.exists("voice_ids.json"):
                with open("voice_ids.json", "r") as f:
                    data = json.load(f)
                    self.voice_embeddings = np.array(data["embeddings"])
                    self.voice_metadata = data["metadata"]
                    self.index.add(self.voice_embeddings)
        except Exception as e:
            logger.error(f"Fehler beim Laden der Voice-IDs: {str(e)}")

    def save_voice_ids(self):
        """Speichert Voice-IDs"""
        try:
            data = {
                "embeddings": self.voice_embeddings.tolist(),
                "metadata": self.voice_metadata,
            }
            with open("voice_ids.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Voice-IDs: {str(e)}")

    def extract_voice_embedding(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Extrahiert Voice-Embedding aus Audiodaten"""
        try:
            # Audio für das Modell vorbereiten
            inputs = self.processor(
                audio, sampling_rate=sr, return_tensors="pt", padding=True
            ).to(self.device)

            # Embedding extrahieren
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

            return embeddings.cpu().numpy()

        except Exception as e:
            logger.error(f"Fehler beim Extrahieren des Voice-Embeddings: {str(e)}")
            raise

    def register_voice(self, audio: np.ndarray, sr: int, metadata: Dict) -> str:
        """Registriert eine neue Stimme"""
        try:
            # Voice-Embedding extrahieren
            embedding = self.extract_voice_embedding(audio, sr)

            # Metadaten hinzufügen
            voice_id = f"voice_{len(self.voice_metadata)}"
            metadata["id"] = voice_id
            metadata["registered_at"] = datetime.now().isoformat()

            # Zum Index hinzufügen
            self.voice_embeddings = (
                np.vstack([self.voice_embeddings, embedding])
                if len(self.voice_embeddings) > 0
                else embedding
            )
            self.voice_metadata.append(metadata)
            self.index.add(embedding)

            # Speichern
            self.save_voice_ids()

            return voice_id

        except Exception as e:
            logger.error(f"Fehler beim Registrieren der Stimme: {str(e)}")
            raise

    def identify_voice(
        self, audio: np.ndarray, sr: int, threshold: float = 0.8
    ) -> List[Dict]:
        """Identifiziert eine Stimme"""
        try:
            # Voice-Embedding extrahieren
            embedding = self.extract_voice_embedding(audio, sr)

            # Ähnlichkeitssuche
            distances, indices = self.index.search(embedding, k=5)

            # Ergebnisse formatieren
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if dist < threshold:
                    result = self.voice_metadata[idx].copy()
                    result["similarity"] = 1 - (dist / threshold)
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Fehler bei der Stimmidentifikation: {str(e)}")
            raise


class FaceIDService:
    def __init__(self):
        self.face_reid_url = "http://face-reid:8000"  # URL zum Face-ReID Service

    def register_face(self, image_data: bytes, metadata: Dict) -> str:
        """Registriert ein neues Gesicht"""
        try:
            # Bild an Face-ReID Service senden
            response = requests.post(
                f"{self.face_reid_url}/register",
                files={"image": image_data},
                data={"metadata": json.dumps(metadata)},
            )
            response.raise_for_status()

            return response.json()["face_id"]

        except Exception as e:
            logger.error(f"Fehler beim Registrieren des Gesichts: {str(e)}")
            raise

    def identify_face(self, image_data: bytes, threshold: float = 0.8) -> List[Dict]:
        """Identifiziert ein Gesicht"""
        try:
            # Bild an Face-ReID Service senden
            response = requests.post(
                f"{self.face_reid_url}/identify",
                files={"image": image_data},
                params={"threshold": threshold},
            )
            response.raise_for_status()

            return response.json()["matches"]

        except Exception as e:
            logger.error(f"Fehler bei der Gesichtsidentifikation: {str(e)}")
            raise


class NoiseType:
    HVAC = "hvac"  # Klimaanlage
    FAN = "fan"  # Ventilator
    TRAFFIC = "traffic"  # Verkehr
    MUSIC = "music"  # Hintergrundmusik
    CROWD = "crowd"  # Menschenmenge
    MACHINE = "machine"  # Maschinen
    WIND = "wind"  # Wind
    RAIN = "rain"  # Regen
    OTHER = "other"  # Sonstige


class EmotionType:
    PLEASURE = "pleasure"
    PAIN = "pain"
    FEAR = "fear"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    SUBMISSION = "submission"
    DOMINANCE = "dominance"
    RESISTANCE = "resistance"
    COMPLIANCE = "compliance"
    NEUTRAL = "neutral"


class WhisperService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.whisper_model = None
        self.emotion_model = None
        self.emotion_processor = None
        self.person_identifier = PersonIdentifier()
        self.batch_size = 4
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.noise_types = [
            NoiseType.HVAC,
            NoiseType.FAN,
            NoiseType.TRAFFIC,
            NoiseType.MUSIC,
            NoiseType.CROWD,
            NoiseType.MACHINE,
            NoiseType.WIND,
            NoiseType.RAIN,
            NoiseType.OTHER,
        ]
        self.emotion_labels = [
            EmotionType.PLEASURE,
            EmotionType.PAIN,
            EmotionType.FEAR,
            EmotionType.ANXIETY,
            EmotionType.EXCITEMENT,
            EmotionType.SUBMISSION,
            EmotionType.DOMINANCE,
            EmotionType.RESISTANCE,
            EmotionType.COMPLIANCE,
            EmotionType.NEUTRAL,
        ]
        self.initialize_models()

    def initialize_models(self):
        """Initialisiert Whisper und Emotionsmodelle"""
        try:
            # Whisper-Modell laden
            self.whisper_model = whisper.load_model("large-v3", device=self.device)

            # Emotionsmodell laden
            self.emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained(
                "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
                num_labels=len(self.emotion_labels),
            ).to(self.device)
            self.emotion_processor = Wav2Vec2FeatureExtractor.from_pretrained(
                "ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
            )

            # Modelle in Evaluierungsmodus setzen
            self.whisper_model.eval()
            self.emotion_model.eval()

            logger.info(f"Modelle erfolgreich initialisiert auf {self.device}")
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Modelle: {str(e)}")
            raise

    def detect_noise(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Erkennt Störgeräusche in Audiodaten"""
        try:
            # Spektrale Analyse
            S = np.abs(librosa.stft(audio))
            freqs = librosa.fft_frequencies(sr=sr)

            # Merkmale extrahieren
            features = {
                "low_freq_energy": np.mean(S[freqs < 100]),
                "mid_freq_energy": np.mean(S[(freqs >= 100) & (freqs < 1000)]),
                "high_freq_energy": np.mean(S[freqs >= 1000]),
                "spectral_flatness": librosa.feature.spectral_flatness(S=S)[0].mean(),
                "zero_crossing_rate": librosa.feature.zero_crossing_rate(audio)[
                    0
                ].mean(),
            }

            # Störgeräusche klassifizieren
            noise_scores = {
                NoiseType.HVAC: features["low_freq_energy"] * 0.7
                + features["spectral_flatness"] * 0.3,
                NoiseType.FAN: features["mid_freq_energy"] * 0.6
                + features["spectral_flatness"] * 0.4,
                NoiseType.TRAFFIC: features["low_freq_energy"] * 0.5
                + features["high_freq_energy"] * 0.5,
                NoiseType.MUSIC: features["spectral_flatness"] * 0.8
                + features["mid_freq_energy"] * 0.2,
                NoiseType.CROWD: features["zero_crossing_rate"] * 0.7
                + features["mid_freq_energy"] * 0.3,
                NoiseType.MACHINE: features["low_freq_energy"] * 0.6
                + features["spectral_flatness"] * 0.4,
                NoiseType.WIND: features["high_freq_energy"] * 0.8
                + features["spectral_flatness"] * 0.2,
                NoiseType.RAIN: features["high_freq_energy"] * 0.7
                + features["zero_crossing_rate"] * 0.3,
                NoiseType.OTHER: features["spectral_flatness"] * 0.5
                + features["zero_crossing_rate"] * 0.5,
            }

            # Normalisierung
            total = sum(noise_scores.values())
            if total > 0:
                noise_scores = {k: v / total for k, v in noise_scores.items()}

            return noise_scores

        except Exception as e:
            logger.error(f"Fehler bei der Störgeräuscherkennung: {str(e)}")
            raise

    def reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Reduziert Störgeräusche in Audiodaten"""
        try:
            # Spektrale Subtraktion
            reduced_audio = nr.reduce_noise(
                y=audio,
                sr=sr,
                prop_decrease=0.75,
                n_fft=2048,
                win_length=2048,
                hop_length=512,
                time_constant_s=2.0,
                freq_mask_smooth_hz=500,
                time_mask_smooth_ms=50,
            )

            # Hochpassfilter für Tieftonunterdrückung
            nyquist = sr / 2
            cutoff = 80  # Hz
            b, a = signal.butter(4, cutoff / nyquist, btype="high")
            reduced_audio = signal.filtfilt(b, a, reduced_audio)

            return reduced_audio

        except Exception as e:
            logger.error(f"Fehler bei der Rauschunterdrückung: {str(e)}")
            raise

    @lru_cache(maxsize=100)
    def load_audio(self, audio_data: bytes) -> Tuple[np.ndarray, int]:
        """Lädt und normalisiert Audiodaten"""
        try:
            audio, sr = sf.read(io.BytesIO(audio_data))
            if sr != 16000:
                audio = whisper.audio.resample(audio, sr, 16000)
                sr = 16000

            # Störgeräusche erkennen
            noise_scores = self.detect_noise(audio, sr)

            # Rauschunterdrückung anwenden wenn nötig
            if (
                max(noise_scores.values()) > 0.3
            ):  # Schwellenwert für Rauschunterdrückung
                audio = self.reduce_noise(audio, sr)

            return audio, sr
        except Exception as e:
            logger.error(f"Fehler beim Laden der Audiodaten: {str(e)}")
            raise

    def detect_emotions(self, audio: np.ndarray) -> Dict[str, float]:
        """Erkennt Emotionen in Audiodaten"""
        try:
            # Audio für Emotionsmodell vorbereiten
            inputs = self.emotion_processor(
                audio, sampling_rate=16000, return_tensors="pt", padding=True
            ).to(self.device)

            # Emotionen vorhersagen
            with torch.no_grad():
                outputs = self.emotion_model(**inputs)
                probabilities = F.softmax(outputs.logits, dim=1)

            # Ergebnisse formatieren
            emotions = {
                label: float(prob)
                for label, prob in zip(self.emotion_labels, probabilities[0])
            }

            return emotions

        except Exception as e:
            logger.error(f"Fehler bei der Emotionserkennung: {str(e)}")
            raise

    def analyze_context(
        self, text: str, emotions: Dict[str, float], noise_scores: Dict[str, float]
    ) -> Dict:
        """Analysiert den Kontext basierend auf Text, Emotionen und Störgeräuschen"""
        try:
            # NSFW/Restraint-spezifische Analyse
            context_analysis = {
                "nsfw_score": 0.0,
                "restraint_score": 0.0,
                "dominance_score": emotions[EmotionType.DOMINANCE],
                "submission_score": emotions[EmotionType.SUBMISSION],
                "resistance_score": emotions[EmotionType.RESISTANCE],
                "compliance_score": emotions[EmotionType.COMPLIANCE],
                "intensity": max(emotions.values()),
                "noise_impact": max(noise_scores.values()),
                "dominant_noise": max(noise_scores.items(), key=lambda x: x[1])[0],
            }

            # Kontextbasierte Gewichtung
            if emotions[EmotionType.PAIN] > 0.5:
                context_analysis["nsfw_score"] += 0.3
            if emotions[EmotionType.SUBMISSION] > 0.5:
                context_analysis["restraint_score"] += 0.4
            if emotions[EmotionType.RESISTANCE] > 0.5:
                context_analysis["restraint_score"] += 0.3

            # Störgeräusche in Kontextanalyse einbeziehen
            if noise_scores[NoiseType.CROWD] > 0.5:
                context_analysis[
                    "nsfw_score"
                ] *= 0.8  # Reduziere NSFW-Score bei Hintergrundgeräuschen
            if noise_scores[NoiseType.MACHINE] > 0.5:
                context_analysis[
                    "restraint_score"
                ] *= 0.9  # Reduziere Restraint-Score bei Maschinengeräuschen

            return context_analysis

        except Exception as e:
            logger.error(f"Fehler bei der Kontextanalyse: {str(e)}")
            raise

    async def process_batch(
        self,
        audio_files: List[bytes],
        face_images: Optional[List[bytes]] = None,
        language: Optional[str] = None,
    ) -> List[Dict]:
        """Verarbeitet einen Batch von Audiodateien und optional Gesichtsbildern"""
        try:
            results = []
            for i, audio_data in enumerate(audio_files):
                # Audiodaten laden und Störgeräusche erkennen
                audio, sr = self.load_audio(audio_data)
                noise_scores = self.detect_noise(audio, sr)

                # Transkription
                with torch.cuda.amp.autocast():
                    transcription = self.whisper_model.transcribe(
                        audio,
                        language=language,
                        fp16=True if self.device == "cuda" else False,
                    )

                # Emotionen erkennen
                emotions = self.detect_emotions(audio)

                # Personenidentifikation
                face_image = (
                    face_images[i] if face_images and i < len(face_images) else None
                )
                person_identification = self.person_identifier.identify_person(
                    voice_audio=audio, voice_sr=sr, face_image=face_image
                )

                # Kontext analysieren
                context = self.analyze_context(
                    transcription["text"], emotions, noise_scores
                )

                # Ergebnisse zusammenführen
                result = {
                    "text": transcription["text"],
                    "segments": transcription["segments"],
                    "emotions": emotions,
                    "noise_analysis": noise_scores,
                    "context_analysis": context,
                    "person_identification": person_identification,
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Fehler bei der Batch-Verarbeitung: {str(e)}")
            raise

    async def transcribe_audio(
        self,
        audio_data: bytes,
        face_image: Optional[bytes] = None,
        language: Optional[str] = None,
    ) -> Dict:
        """Transkribiert eine Audiodatei mit Emotionsanalyse und Personenidentifikation"""
        try:
            results = await self.process_batch(
                [audio_data], [face_image] if face_image else None, language
            )
            return results[0]
        except Exception as e:
            logger.error(f"Fehler bei der Transkription: {str(e)}")
            raise

    async def transcribe_batch(
        self,
        audio_files: List[bytes],
        face_images: Optional[List[bytes]] = None,
        language: Optional[str] = None,
    ) -> List[Dict]:
        """Transkribiert einen Batch von Audiodateien mit optionalen Gesichtsbildern"""
        try:
            batches = [
                audio_files[i : i + self.batch_size]
                for i in range(0, len(audio_files), self.batch_size)
            ]
            face_batches = (
                [
                    face_images[i : i + self.batch_size]
                    for i in range(0, len(face_images), self.batch_size)
                ]
                if face_images
                else None
            )
            tasks = [
                self.process_batch(
                    batch, face_batch if face_batches else None, language
                )
                for batch, face_batch in zip(
                    batches, face_batches if face_batches else [None] * len(batches)
                )
            ]
            results = await asyncio.gather(*tasks)
            return [item for sublist in results for item in sublist]
        except Exception as e:
            logger.error(f"Fehler bei der Batch-Transkription: {str(e)}")
            raise


# Service-Instanz erstellen
whisper_service = WhisperService()


class TranscriptionRequest(BaseModel):
    audio_data: bytes
    face_image: Optional[bytes] = None
    language: Optional[str] = None


class BatchTranscriptionRequest(BaseModel):
    audio_files: List[bytes]
    face_images: Optional[List[bytes]] = None
    language: Optional[str] = None


class PersonRegistrationRequest(BaseModel):
    voice_audio: bytes
    face_image: Optional[bytes] = None
    metadata: Dict


@app.post("/transcribe")
async def transcribe_audio(request: TranscriptionRequest):
    """Transkribiert eine Audiodatei mit Emotionsanalyse und Personenidentifikation"""
    try:
        return await whisper_service.transcribe_audio(
            request.audio_data, request.face_image, request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe/batch")
async def transcribe_batch(request: BatchTranscriptionRequest):
    """Transkribiert einen Batch von Audiodateien mit optionalen Gesichtsbildern"""
    try:
        return await whisper_service.transcribe_batch(
            request.audio_files, request.face_images, request.language
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/person/register")
async def register_person(request: PersonRegistrationRequest):
    """Registriert eine neue Person mit Stimme und optionalem Gesicht"""
    try:
        audio, sr = whisper_service.load_audio(request.voice_audio)
        person_id = whisper_service.person_identifier.register_person(
            voice_audio=audio,
            voice_sr=sr,
            face_image=request.face_image,
            metadata=request.metadata,
        )
        return {"person_id": person_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    return {
        "status": "healthy",
        "device": whisper_service.device,
        "batch_size": whisper_service.batch_size,
        "models": {
            "whisper": "large-v3",
            "emotion": "wav2vec2-lg-xlsr-en-speech-emotion-recognition",
            "voice_id": "wav2vec2-base-960h",
            "face_id": "face-reid-service",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# 📊 Project Status – AI Media Analysis

**Last updated:** 2025-05-29  
**Maintainer:** [Paddel87](https://github.com/Paddel87)

---

## ✅ Current Modules in `/services/`

| Module             | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `control`          | Orchestration layer (startup logic, job monitoring, Prefect integration)   |
| `embedding_server` | Dummy for future ArcFace / OSNet ReID embedding APIs                        |
| `llm_summarizer`   | Interface to Gemini Flash & fallback LLMs via API                           |
| `object_review`    | Human-in-the-loop module for object labeling & learning                     |
| `ui`               | Streamlit-based frontend for manual ID editing and visual output            |
| `vector_db`        | Qdrant-compatible vector database                                            |
| `vision_pipeline`  | Main processing pipeline (video/image ingest, detection, speech, OCR, etc.) |

---

## 🧠 Features Implemented

- [x] Modular microservice architecture
- [x] Docker-ready structure for each service
- [x] Redis/Queue-based auto-scaling (planned via control module)
- [x] OpenLLM-compatible fallback system (Anthropic/OpenAI supported)
- [x] Manual override and learning via object review module
- [x] Full support for both video files and image series

---

## 🧩 Pending Tasks

- [ ] Integrate real ArcFace / OSNet models into `embedding_server`
- [ ] Finalize LLM summarizer prompt templates and token usage tracking
- [ ] Expand OCR detection to multi-language subtitle regions
- [ ] Define internal API schemas between services
- [ ] Deployment testing on Node C (VPS 1000 G11 @ Netcup)
- [ ] Logging & monitoring setup (Prefect, Prometheus optional)

---

## 🚧 Notes

- This project is still **pre-deployment** and **never run in production**.
- First live test will occur **after VPS deployment**.
- GitHub repository is private. The operator is solely responsible for use.


| `vision_pipeline`   | Core module: person detection, tracking, NSFW detection, OCR, STT          |
| `object_review`     | Manual object validation & vocabulary learning                             |

## 📂 Recent Additions

- OCR-based logo/title recognition (May 2025)
- Static image sequence analysis support (May 2025)

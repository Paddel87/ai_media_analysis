"""
FastAPI Web-Interface für die Erkenntnisse-Suche.
Einfache Meta-Suche in allen gespeicherten Analyseergebnissen.
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import der Insights-Services - Docker-kompatibel
try:
    from services.common.insights_service import insights_service, InsightType
except ImportError:
    # Fallback für lokale Entwicklung
    sys.path.append("../")
    from common.insights_service import insights_service, InsightType

app = FastAPI(
    title="🔍 AI Media Analysis - Erkenntnisse-Suche",
    description="Durchsuchbare Datenbank aller AI-Analyseergebnisse",
    version="1.0.0"
)


class SearchRequest(BaseModel):
    """Request-Modell für die Suche."""
    search_text: Optional[str] = None
    insight_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    job_id: Optional[str] = None
    limit: int = 50


class SearchResponse(BaseModel):
    """Response-Modell für Suchergebnisse."""
    total_results: int
    results: List[Dict[str, Any]]
    search_info: Dict[str, Any]


@app.get("/", response_class=HTMLResponse)
async def get_search_interface():
    """Liefert eine einfache HTML-Suchoberfläche."""
    html_content = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🔍 AI Media Analysis - Erkenntnisse-Suche</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f7fa;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .search-container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #333;
            }
            input, select, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                font-size: 14px;
            }
            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #007bff;
            }
            .btn {
                background-color: #007bff;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
            }
            .btn:hover {
                background-color: #0056b3;
            }
            .results {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            .result-item {
                border-bottom: 1px solid #e1e5e9;
                padding: 15px 0;
            }
            .result-item:last-child {
                border-bottom: none;
            }
            .result-type {
                background-color: #e9ecef;
                color: #495057;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                display: inline-block;
                margin-bottom: 8px;
            }
            .result-title {
                font-weight: 600;
                color: #333;
                margin-bottom: 5px;
            }
            .result-description {
                color: #666;
                margin-bottom: 8px;
            }
            .result-meta {
                font-size: 12px;
                color: #999;
            }
            .dashboard {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .metric-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            .metric-value {
                font-size: 2em;
                font-weight: bold;
                color: #007bff;
            }
            .metric-label {
                color: #666;
                margin-top: 5px;
            }
            .filters {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 AI Media Analysis - Erkenntnisse-Suche</h1>
            <p>Durchsuchen Sie alle gespeicherten Analyseergebnisse</p>
        </div>

        <div id="dashboard" class="dashboard"></div>

        <div class="search-container">
            <h2>🔧 Suche</h2>
            <form id="searchForm">
                <div class="filters">
                    <div class="form-group">
                        <label for="searchText">Volltext-Suche:</label>
                        <input type="text" id="searchText" name="searchText"
                               placeholder="Suchbegriff eingeben...">
                    </div>

                    <div class="form-group">
                        <label for="insightTypes">Analyse-Typ:</label>
                        <select id="insightTypes" name="insightTypes" multiple>
                            <option value="person_detection">Personenerkennung</option>
                            <option value="emotion_analysis">Emotionsanalyse</option>
                            <option value="restraint_detection">Restraint-Erkennung</option>
                            <option value="clothing_analysis">Kleidungsanalyse</option>
                            <option value="audio_transcription">Audio-Transkription</option>
                            <option value="video_context">Video-Kontext</option>
                            <option value="nsfw_detection">NSFW-Erkennung</option>
                            <option value="object_detection">Objekterkennung</option>
                            <option value="ocr_text">OCR-Text</option>
                            <option value="pose_estimation">Pose-Schätzung</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="tags">Tags (komma-getrennt):</label>
                        <input type="text" id="tags" name="tags"
                               placeholder="tag1, tag2, tag3">
                    </div>

                    <div class="form-group">
                        <label for="limit">Max. Ergebnisse:</label>
                        <select id="limit" name="limit">
                            <option value="10">10</option>
                            <option value="25">25</option>
                            <option value="50" selected>50</option>
                            <option value="100">100</option>
                            <option value="200">200</option>
                        </select>
                    </div>
                </div>

                <button type="submit" class="btn">🔍 Suchen</button>
            </form>
        </div>

        <div id="results" class="results" style="display: none;"></div>

        <script>
            // Dashboard laden
            async function loadDashboard() {
                try {
                    const response = await fetch('/api/summary');
                    const summary = await response.json();

                    const dashboard = document.getElementById('dashboard');
                    dashboard.innerHTML = `
                        <div class="metric-card">
                            <div class="metric-value">${summary.total_insights}</div>
                            <div class="metric-label">Gesamt Erkenntnisse</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${Object.keys(summary.by_insight_type || {}).length}</div>
                            <div class="metric-label">Analyse-Typen</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${Object.keys(summary.by_media_type || {}).length}</div>
                            <div class="metric-label">Medientypen</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">${summary.latest_insight ? 'Aktuell' : 'Keine'}</div>
                            <div class="metric-label">Neueste Erkenntnis</div>
                        </div>
                    `;
                } catch (error) {
                    console.error('Dashboard-Fehler:', error);
                }
            }

            // Suche durchführen
            async function performSearch(params) {
                try {
                    const url = new URL('/api/search', window.location.origin);

                    // Parameter hinzufügen
                    if (params.search_text) url.searchParams.append('search_text', params.search_text);
                    if (params.insight_types && params.insight_types.length > 0) {
                        params.insight_types.forEach(type => url.searchParams.append('insight_types', type));
                    }
                    if (params.tags && params.tags.length > 0) {
                        params.tags.forEach(tag => url.searchParams.append('tags', tag));
                    }
                    if (params.limit) url.searchParams.append('limit', params.limit);

                    const response = await fetch(url);
                    const data = await response.json();

                    displayResults(data);
                } catch (error) {
                    console.error('Suche-Fehler:', error);
                    document.getElementById('results').innerHTML = '<p>Fehler bei der Suche</p>';
                }
            }

            // Ergebnisse anzeigen
            function displayResults(data) {
                const resultsDiv = document.getElementById('results');
                resultsDiv.style.display = 'block';

                if (data.total_results === 0) {
                    resultsDiv.innerHTML = '<h3>🚫 Keine Ergebnisse gefunden</h3>';
                    return;
                }

                let html = `<h3>✅ ${data.total_results} Ergebnisse gefunden</h3>`;

                data.results.forEach(result => {
                    const createdAt = new Date(result.created_at).toLocaleString('de-DE');
                    const tags = result.tags ? result.tags.slice(0, 3).map(tag => `<code>${tag}</code>`).join(' ') : '';

                    html += `
                        <div class="result-item">
                            <div class="result-type">${result.insight_type}</div>
                            <div class="result-title">${result.title}</div>
                            <div class="result-description">${result.description}</div>
                            <div class="result-meta">
                                📁 ${result.media_filename} |
                                🎯 Konfidenz: ${(result.confidence * 100).toFixed(1)}% |
                                📅 ${createdAt}
                                ${tags ? ' | 🏷️ ' + tags : ''}
                            </div>
                        </div>
                    `;
                });

                resultsDiv.innerHTML = html;
            }

            // Form-Handler
            document.getElementById('searchForm').addEventListener('submit', function(e) {
                e.preventDefault();

                const formData = new FormData(e.target);
                const searchText = formData.get('searchText');
                const insightTypes = Array.from(document.getElementById('insightTypes').selectedOptions)
                    .map(option => option.value);
                const tagsInput = formData.get('tags');
                const tags = tagsInput ? tagsInput.split(',').map(tag => tag.trim()).filter(tag => tag) : [];
                const limit = formData.get('limit');

                const params = {
                    search_text: searchText,
                    insight_types: insightTypes,
                    tags: tags,
                    limit: limit
                };

                performSearch(params);
            });

            // Dashboard beim Laden initialisieren
            loadDashboard();
        </script>
    </body>
    </html>
    """
    return html_content


@app.get("/api/search", response_model=SearchResponse)
async def search_insights(
    search_text: Optional[str] = Query(None, description="Volltext-Suche"),
    insight_types: Optional[List[str]] = Query(None, description="Analyse-Typen"),
    tags: Optional[List[str]] = Query(None, description="Tags"),
    start_date: Optional[datetime] = Query(None, description="Start-Datum"),
    end_date: Optional[datetime] = Query(None, description="End-Datum"),
    job_id: Optional[str] = Query(None, description="Job-ID"),
    limit: int = Query(50, description="Max. Ergebnisse", ge=1, le=1000)
):
    """API-Endpoint für die Erkenntnisse-Suche."""

    try:
        results = insights_service.search_insights(
            search_text=search_text,
            insight_types=insight_types,
            tags=tags,
            start_date=start_date,
            end_date=end_date,
            job_id=job_id,
            limit=limit
        )

        return SearchResponse(
            total_results=len(results),
            results=results,
            search_info={
                "search_text": search_text,
                "insight_types": insight_types,
                "tags": tags,
                "limit": limit
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suche fehlgeschlagen: {str(e)}")


@app.post("/api/search", response_model=SearchResponse)
async def search_insights_post(request: SearchRequest):
    """POST-Endpoint für erweiterte Suche."""

    try:
        results = insights_service.search_insights(
            search_text=request.search_text,
            insight_types=request.insight_types,
            tags=request.tags,
            start_date=request.start_date,
            end_date=request.end_date,
            job_id=request.job_id,
            limit=request.limit
        )

        return SearchResponse(
            total_results=len(results),
            results=results,
            search_info={
                "search_text": request.search_text,
                "insight_types": request.insight_types,
                "tags": request.tags,
                "limit": request.limit
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suche fehlgeschlagen: {str(e)}")


@app.get("/api/summary")
async def get_insights_summary():
    """Gibt eine Zusammenfassung aller Erkenntnisse zurück."""

    try:
        return insights_service.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary fehlgeschlagen: {str(e)}")


@app.get("/api/job/{job_id}")
async def get_job_insights(job_id: str):
    """Gibt alle Erkenntnisse für einen Job zurück."""

    try:
        results = insights_service.get_job_insights(job_id)
        return {"job_id": job_id, "total_insights": len(results), "insights": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job-Insights fehlgeschlagen: {str(e)}")


@app.get("/api/media/{media_id}")
async def get_media_insights(media_id: str):
    """Gibt alle Erkenntnisse für ein Medium zurück."""

    try:
        results = insights_service.get_media_insights(media_id)
        return {"media_id": media_id, "total_insights": len(results), "insights": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Media-Insights fehlgeschlagen: {str(e)}")


@app.get("/api/types")
async def get_insight_types():
    """Gibt alle verfügbaren Insight-Typen zurück."""

    return {
        "insight_types": [
            {"value": t.value, "label": t.value.replace("_", " ").title()}
            for t in InsightType
        ]
    }


@app.delete("/api/job/{job_id}")
async def delete_job_insights(job_id: str):
    """Löscht alle Erkenntnisse für einen Job."""
    try:
        deleted_count = insights_service.delete_job_insights(job_id)
        return {
            "message": f"Job {job_id} Erkenntnisse gelöscht",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen: {str(e)}")


@app.get("/health")
async def health_check():
    """Health Check für Service-Monitoring."""
    return {"status": "healthy", "service": "insights_api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

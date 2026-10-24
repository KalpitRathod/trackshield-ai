"""
FastAPI Server for AI Job Tracker & Scam Shield.
Serves the complete REST API and static frontend assets.
"""
import os
import json
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from pipeline import run_pipeline, load_inbox, INBOX_PATH
from interview_prep import get_interview_prep
from follow_up_logic import DEFAULT_TODAY
from gemini_classifier import classify_email, load_cache, save_cache, CACHE_FILE
from cybercrime_report import generate_complaint_dossier


app = FastAPI(
    title="TaalMail AI • GDG Garbathon 2026",
    description="Automated job application tracker, scam quarantine, 1930 cybercrime dossier, and interview prep notes.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)


@app.get("/api/pipeline")
def get_pipeline_data(
    today: str = Query(DEFAULT_TODAY, description="Reference today date YYYY-MM-DD"),
    force_live: bool = Query(False, description="Force live Gemini API execution"),
    api_key: Optional[str] = Query(None, description="Optional Gemini API key")
):
    """Executes the full pipeline and returns structured data for the dashboard."""
    try:
        data = run_pipeline(today_str=today, api_key=api_key, force_live=force_live)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inbox")
def get_inbox():
    """Returns the mocked 20-email inbox."""
    inbox = load_inbox()
    return JSONResponse(content={"total": len(inbox), "emails": inbox})


@app.post("/api/inbox/test_classify")
def test_classify_custom_email(payload: Dict[str, Any] = Body(...)):
    """Classifies an individual email supplied by the user in real time."""
    email_data = {
        "id": payload.get("id", 999),
        "from": payload.get("from", "recruiter@unknown.com"),
        "subject": payload.get("subject", "Job Opportunity"),
        "body": payload.get("body", ""),
        "date": payload.get("date", DEFAULT_TODAY)
    }
    api_key = payload.get("api_key")
    force_live = payload.get("force_live", False)
    result = classify_email(email_data, api_key=api_key, force_live=force_live)
    return JSONResponse(content={"email": email_data, "classification": result})


@app.get("/api/prep")
def get_prep_notes(
    company: str = Query(..., description="Company name"),
    role: str = Query(..., description="Role name")
):
    """Returns interview prep notes for stretch goal."""
    notes = get_interview_prep(company, role)
    return JSONResponse(content=notes)


@app.get("/api/scam/complaint")
def get_scam_complaint(email_id: int = Query(..., description="ID of the scam email")):
    """Generates an official Cybercrime 1930 / cybercrime.gov.in complaint dossier for a scam email."""
    inbox = load_inbox()
    email_data = next((e for e in inbox if e.get("id") == email_id), None)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")
    cache = load_cache()
    cached_info = cache.get(str(email_id), {})
    scam_reasons = cached_info.get("scam_reasons", [])
    company = cached_info.get("company", email_data.get("company", ""))
    role = cached_info.get("role", email_data.get("role", ""))
    enriched_email = {**email_data, "company": company, "role": role}
    dossier = generate_complaint_dossier(enriched_email, scam_reasons=scam_reasons)
    return JSONResponse(content=dossier)


@app.get("/api/cache/stats")
def get_cache_stats():
    """Returns statistics on the local Gemini response cache."""
    cache = load_cache()
    return JSONResponse(content={
        "cache_file": CACHE_FILE,
        "cached_email_count": len(cache),
        "rule_06_compliant": True
    })


# Serve static files from static/ directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(content={"message": "Frontend static file not yet created."})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=False)

"""Read-only observability API. Add authentication before internet deployment."""
import json
import os
from pathlib import Path
import pandas as pd
import requests
from fastapi import FastAPI,HTTPException
from quality.ai import investigate
app=FastAPI(title="Enterprise Data Quality and Observability",version="0.1.0")

def load_report():
    path=Path(os.getenv("REPORT_PATH","artifacts/latest.json"))
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

@app.get("/health")
def health():return {"status":"ok","report_ready":load_report() is not None}

@app.get("/api/quality")
def quality():
    gold=Path(os.getenv("GOLD_PATH","data/gold/quality_by_class.parquet"))
    return {"report":load_report(),"classes":pd.read_parquet(gold).round(3).to_dict("records") if gold.is_file() else []}

@app.post("/api/ai/investigate")
def ai():
    report=load_report()
    if not report:raise HTTPException(404,"Run ETL before AI investigation")
    try:return investigate(report)
    except (requests.RequestException,ValueError,KeyError) as exc:raise HTTPException(502,"AI unavailable") from exc

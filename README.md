# ROI Calculator Backend

## Overview
- Python + FastAPI backend that replicates Excel-style ROI calculations in pure Python.
- Accepts structured JSON and returns ROI metrics plus a base64 PDF report.
- Endpoints: `POST /roi`, `POST /roi/report`.

## Run Locally (Python)
- Create a venv and install deps:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
- Start the server:
  - `uvicorn app.main:app --reload --port 8000`
- Open docs: `http://localhost:8000/docs`

### Example /roi
```
curl -s -X POST 'http://localhost:8000/roi' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_name": "Acme Inc",
    "industry": "Manufacturing",
    "revenue": 100000000,
    "cogs_pct": 0.60,
    "logistics_cost_pct": 0.08,
    "exception_cost_pct": 0.02,
    "avg_inventory_value": null,
    "logistics_planner_fte": 10
  }'
```

### Example /roi/report (save PDF)
```
curl -s -X POST 'http://localhost:8000/roi/report' \
  -H 'Content-Type: application/json' \
  -d '{
    "company_name": "Acme Inc",
    "industry": "Manufacturing",
    "revenue": 100000000,
    "cogs_pct": 0.60,
    "logistics_cost_pct": 0.08,
    "exception_cost_pct": 0.02,
    "avg_inventory_value": null,
    "logistics_planner_fte": 10
  }' \
| python3 -c 'import sys, json, base64; r=json.load(sys.stdin); open(r["filename"],"wb").write(base64.b64decode(r["pdf_base64"])); print("Saved", r["filename"])'
```

## Run with Docker
- Build: `docker build -t roi-backend:latest .`
- Run: `docker run -p 8000:8000 roi-backend:latest`
- Test: `http://localhost:8000/docs`

## What It Does
- Computes derived metrics (COGS, logistics/exception cost, inventory value).
- Calculates recurring EBIT savings, cost avoidance, and one-time cash benefits.
- Returns final ROI percentage and payback months.
- Generates a PDF summary with tables and a savings bar chart.

## Input Schema
```
{
  "company_name": "string",
  "industry": "string",
  "revenue": number,
  "cogs_pct": number,
  "logistics_cost_pct": number,
  "exception_cost_pct": number,
  "avg_inventory_value": number|null,
  "logistics_planner_fte": number|null
}
```

## Project Structure
- `requirements.txt` — dependencies
- `app/main.py` — FastAPI app and endpoints
- `app/models.py` — Pydantic models
- `app/config.py` — industry benchmark constants
- `app/roi_engine.py` — pure-Python ROI logic
- `app/pdf_generator.py` — HTML to PDF with chart
- `Dockerfile`, `.dockerignore`, `DEPLOY_DOCKER_GITHUB.md`
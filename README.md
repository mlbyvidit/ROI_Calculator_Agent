# ROI Calculator Backend

## Overview
- Python + FastAPI backend that calculates ROI in pure Python.
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

## Live Service
- Chat UI: https://roi-calculator-agent.onrender.com/
- API docs: https://roi-calculator-agent.onrender.com/docs

## Chatbot (Mistral + /chat)
- Adds a conversational assistant that gathers ROI inputs and, when confirmed, computes ROI and returns a downloadable PDF.
- Frontend served at `/` provides a chat UI and a “Download ROI PDF” button when the PDF is ready.

### Setup API Key
- Create a `.env` file in the project root with:
  - `MISTRAL_API_KEY=<your_real_mistral_key>`
- The app automatically loads `.env` via `python-dotenv`.

### Run Locally
- With venv:
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`
- Open chat UI: `http://localhost:8000/`

### Run in Docker
- Ensure `.env` exists with your key.
- `docker build -t roi-backend:latest .`
- `docker run --rm -d --env-file .env -p 8000:8000 roi-backend:latest`
- Open chat UI: `http://localhost:8000/`

### /chat API Example
```
curl -s -X POST 'http://localhost:8000/chat' \
  -H 'Content-Type: application/json' \
  -d '{ "messages": [ { "role": "user", "content": "We are Acme in Manufacturing. Revenue 100M, COGS 60%, Logistics 8%, Exceptions 2%, Planners 10." } ] }' \
| python3 -m json.tool
```
- The assistant asks follow-ups for missing values.
- Once confirmed, the response includes `metrics`, `pdf_base64`, and `filename`.

### Troubleshooting
- Missing key message: add `MISTRAL_API_KEY` to `.env` and restart the server/container.
- Rate limit or capacity: change `MODEL_NAME` in `app/llm_client.py` (e.g., `mistral-tiny`, `mistral-small-latest`).
- Port conflicts: stop any process using `8000`.

### Deploy to Render
- Connect the GitHub repo and create a service from `render.yaml`.
- In the service, add Environment Variable `MISTRAL_API_KEY` with your real key.
- Open the Render URL for the chat UI and docs.

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

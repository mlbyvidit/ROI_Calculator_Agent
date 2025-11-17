# Deployment and Environment Setup

## Local Development
- Create a `.env` file in the project root:
  - `MISTRAL_API_KEY=<your_real_key>`
- Install dependencies and run:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - `uvicorn app.main:app --reload --port 8000`
- Test chat UI at `http://localhost:8000/` or API at `http://localhost:8000/docs`.

## Docker
- Put your key in `.env`:
  - `MISTRAL_API_KEY=<your_real_key>`
- Build and run:
  - `docker build -t roi-backend:latest .`
  - `docker run --env-file .env -p 8000:8000 roi-backend:latest`
- Open `http://localhost:8000/`.

## Render
- After creating the service (via repo import or `render.yaml` blueprint):
  - Go to your service → Settings → Environment Variables.
  - Add key `MISTRAL_API_KEY` with your real value.
  - Save and redeploy.

## Notes
- Do not commit real API keys. Use `.env.example` as a template.
- The `/chat` endpoint requires a valid `MISTRAL_API_KEY`; otherwise, the agent will not call the LLM and only proceeds if the user message includes the `ACTION:CALL_BACKEND` block.
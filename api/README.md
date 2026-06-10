# API (FastAPI)

This directory contains the backend API for the AI Interviewer Chatbot MVP.

## Step 1 scope

- FastAPI app skeleton
- `GET /health` endpoint
- Local frontend CORS configuration
- Environment config loading from `.env`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Manual test

In a separate terminal:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

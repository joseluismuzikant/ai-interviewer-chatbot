# API (FastAPI)

This directory contains the backend API for the AI Interviewer Chatbot MVP.

## Step 1 + Step 3 scope

- FastAPI app skeleton
- `GET /health` endpoint
- Local frontend CORS configuration
- Environment config loading from `.env`
- Supabase client wiring (service-role key)
- `POST /interviews`
- `GET /interviews/{interview_id}`

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Before calling interview endpoints, fill `.env` with:

```env
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
```

## Supabase setup (Step 3)

1. Open your Supabase project SQL editor.
2. Copy/paste `docs/supabase_schema.sql`.
3. Run the script to create `interviews` and `messages` tables.

## Manual test

In a separate terminal:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Create interview:

```bash
curl -X POST http://localhost:8000/interviews \
  -H "Content-Type: application/json" \
  -d '{"title":"Backend Engineer","target_questions":8,"starting_difficulty":5}'
```

Get interview:

```bash
curl http://localhost:8000/interviews/<interview_id>
```

Expected: returns the interview record by id, or `404` if it does not exist.

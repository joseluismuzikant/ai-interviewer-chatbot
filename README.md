# AI Interviewer Chatbot (MVP)

A local-first MVP for running adaptive, AI-assisted technical interviews.

This project is being built step-by-step from the blueprint in `docs/AI-Interview-Chatbot-Blueprint 2.pdf`, using:

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + Python
- Database (next steps): Supabase PostgreSQL
- Storage (next steps): Supabase Storage
- LLM (next steps): OpenAI API (`gpt-4o-mini` by default)

## Vision

The intended end-to-end flow is:

1. Admin creates interview
2. Admin uploads resume and role description
3. Backend extracts text and runs match analysis
4. Candidate starts interview session
5. System asks adaptive questions
6. Candidate answers are scored with a rubric
7. Difficulty adjusts over time
8. Final report is generated

This MVP emphasizes deterministic orchestration around LLM calls, structured JSON outputs, and persistence of interview transcripts and scoring metadata.

## Current Status

Implemented now:

- Backend skeleton with FastAPI
- Health endpoint: `GET /health`
- Backend CORS for local frontend origins
- Environment-driven backend configuration via `.env`
- Frontend skeleton with route structure and placeholder pages
- Frontend API client configured via `VITE_API_URL`

Not implemented yet (planned):

- Supabase schema + persistence
- Document upload + text extraction
- Match analysis endpoint
- Interview loop (start, answer, next-question)
- Scoring + difficulty adaptation
- Final report generation
- Docker setup for local orchestration

## Architecture (MVP)

```mermaid
flowchart LR
  A[Admin UI] -->|REST| B[FastAPI Orchestrator]
  C[Candidate UI] -->|REST| B
  B --> D[(Supabase PostgreSQL)]
  B --> E[(Supabase Storage)]
  B --> F[OpenAI API]
```

## Repository Layout

```text
ai-interviewer-chatbot/
├── AGENTS.md
├── README.md
├── api/
│   ├── README.md
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── schemas.py
│       ├── llm.py
│       ├── interview_service.py
│       └── document_service.py
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── .env.example
│   └── src/
│       ├── App.tsx
│       ├── api/client.ts
│       └── pages/
└── docs/
    └── AI-Interview-Chatbot-Blueprint 2.pdf
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

## Quick Start (Local)

### 1) Start the API

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API runs at: `http://localhost:8000`

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### 2) Start the Frontend

Open a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend typically runs at: `http://localhost:5173`

## Environment Variables

### API (`api/.env`)

Based on `api/.env.example`:

- `SUPABASE_URL=`
- `SUPABASE_SERVICE_ROLE_KEY=`
- `OPENAI_API_KEY=`
- `OPENAI_MODEL=gpt-4o-mini`

Note: these are scaffolded now and will be used in upcoming steps.

### Frontend (`frontend/.env`)

Based on `frontend/.env.example`:

- `VITE_API_URL=http://localhost:8000`

## Available Routes and Endpoints

### Backend

- `GET /health` -> returns service health

### Frontend

- `/admin`
- `/admin/interviews/:id`
- `/interview/:id`

## Product Workflow (Blueprint-Aligned)

Target state machine:

- `DRAFT` -> `READY` -> `IN_PROGRESS` -> `COMPLETED`

Planned core workflows:

1. Create + analyze interview
2. Run adaptive interview loop
3. Generate final report

The implementation roadmap is defined in `AGENTS.md` (Steps 1-11).

## Development Notes

- Keep the MVP simple; avoid premature abstraction.
- Favor strict JSON contracts for LLM outputs.
- Persist transcripts and scoring metadata for report generation.
- Treat integrity signals (`response_time_ms`, `paste_detected`) as informational, not automatic disqualifiers.

## Documentation

- Blueprint: `docs/AI-Interview-Chatbot-Blueprint 2.pdf`
- Backend notes: `api/README.md`
- Frontend notes: `frontend/README.md`
- Step-by-step implementation plan: `AGENTS.md`

## Next Milestones

1. Supabase schema + backend interview endpoints
2. Document upload and extraction
3. Match analysis with OpenAI
4. Interview start + answer scoring loop
5. Final report generation
6. Dockerize API + frontend for local runs

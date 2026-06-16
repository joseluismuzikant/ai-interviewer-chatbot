# API (FastAPI)

This directory contains the backend API for the AI Interviewer Chatbot MVP.

## Implemented scope

- FastAPI app skeleton
- `GET /health` endpoint
- Local frontend CORS configuration
- Environment config loading from `.env`
- Supabase client wiring (service-role key)
- `POST /interviews`
- `GET /interviews`
- `GET /interviews/{interview_id}`
- `DELETE /interviews/{interview_id}`
- `POST /interviews/{interview_id}/documents` (PDF upload)
- `GET /interviews/{interview_id}/documents` (from documents table)
- `GET /interviews/{interview_id}/documentsFromStorage` (from Supabase Storage)
- `DELETE /interviews/{interview_id}/documents/{filename}`
- PDF text extraction with PyMuPDF
- File upload to Supabase Storage bucket `interview-documents`
- Upsert document metadata/content into `documents` table
- Filename normalization to `snake_case` before storing in Storage and DB
- `POST /interviews/{interview_id}/analyze` (LLM match analysis)
- `POST /interviews/{interview_id}/start` (start candidate interview)
- `POST /interviews/{interview_id}/answer` (score answer + generate next question)
- `GET /interviews/{interview_id}/messages` (ordered transcript)
- `POST /interviews/{interview_id}/report` (generate and persist final report)
- `GET /interviews/{interview_id}/report` (fetch persisted final report)
- Multi-provider LLM factory (`mock`, `openai`, `gemini`, `deepseek`)
- Clean HTTP 503 error handling for LLM provider failures (e.g. DeepSeek insufficient balance)
- Strict LLM JSON validation for match analysis, generated questions, answer evaluation, and final report fields

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
LLM_PROVIDER=mock
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
GOOGLE_API_KEY=...
GOOGLE_MODEL=gemini-2.0-flash
DEEPSEEK_API_KEY=...
DEEPSEEK_MODEL=deepseek-chat
```

## Supabase setup (Step 3)

1. Open your Supabase project SQL editor.
2. Copy/paste `docs/supabase_schema.sql`.
3. Run the script to create `interviews`, `messages`, and `documents` tables.

## Supabase Storage setup (Step 5)

1. Open Supabase Storage.
2. Create a bucket named `interview-documents`.
3. Keep it private for MVP testing.

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

Upload document (PDF only):

```bash
curl -X POST http://localhost:8000/interviews/<interview_id>/documents \
  -F "document_type=resume" \
  -F "file=@/absolute/path/to/resume.pdf;type=application/pdf"
```

Use `document_type=role_description` for the role description upload.

List all interviews:

```bash
curl http://localhost:8000/interviews
```

Delete interview:

```bash
curl -X DELETE -i http://localhost:8000/interviews/<interview_id>
```

List documents from table (includes extracted text):

```bash
curl http://localhost:8000/interviews/<interview_id>/documents
```

List documents from storage:

```bash
curl http://localhost:8000/interviews/<interview_id>/documentsFromStorage
```

Delete document by filename:

```bash
curl -X DELETE \
  "http://localhost:8000/interviews/<interview_id>/documents/<filename.pdf>"
```

Run match analysis:

```bash
curl -X POST http://localhost:8000/interviews/<interview_id>/analyze
```

Start interview:

```bash
curl -X POST http://localhost:8000/interviews/<interview_id>/start
```

Get interview messages:

```bash
curl http://localhost:8000/interviews/<interview_id>/messages
```

Submit candidate answer:

```bash
curl -X POST http://localhost:8000/interviews/<interview_id>/answer \
  -H "Content-Type: application/json" \
  -d '{"answer":"I would design clear resource-oriented endpoints with strong validation and observability.","response_time_ms":45000,"paste_detected":false}'
```

Generate final report:

```bash
curl -X POST http://localhost:8000/interviews/<interview_id>/report
```

Get final report:

```bash
curl http://localhost:8000/interviews/<interview_id>/report
```

Example final report response shape:

```json
{
  "summary": "string",
  "overall_score": 7.2,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "integrity_notes": ["string"],
  "recommendation": "YES",
  "recommendation_rationale": "string"
}
```

## Step 9 report behavior

- Report generation requires interview status `COMPLETED`.
- `overall_score` is calculated in application code (average of candidate `answer_quality_score`, rounded to 1 decimal).
- `integrity_notes` are calculated in application code from `paste_detected` and response-time-vs-length heuristics.
- LLM generates only summary/recommendation content fields via `generate_report(context)`.
- Report is persisted into `interviews.report_json`.
- `GET /report` returns persisted report or `404` if none exists yet.

Notes:

- Upload endpoint normalizes filename to `snake_case` before saving.
- Upload endpoint replaces previous documents of the same type (effectively an upsert).
- LLM Provider is controlled by `LLM_PROVIDER` in `.env` (options: `mock`, `openai`, `gemini`, `deepseek`).
- Invalid first-question JSON from any provider returns `503` with `LLM returned invalid question JSON.`
- Invalid answer-evaluation JSON from any provider returns `503` with `LLM returned invalid answer evaluation JSON.`
- Invalid final-report JSON from any provider returns `503` with `LLM returned invalid report JSON.`

## Architecture (Onion / Step 12)

The backend follows an Onion Architecture with four concentric layers:

```text
api/app/
├── core/                 # Cross-cutting: config, LLM provider factory
├── domain/               # Enterprise business rules (abstract interfaces)
│   └── interfaces/
├── application/          # Application business rules (use cases / services)
│   └── use_cases/
├── infrastructure/       # External adapters (Supabase, LLM providers)
│   ├── data/
│   └── llm/
└── presentation/         # HTTP layer (controllers, Pydantic schemas, DI)
    ├── controllers/
    ├── schemas/
    └── dependencies.py

Dependency direction:
  domain ← application ← infrastructure → domain
  domain ← presentation → application → infrastructure
```

- No layer imports from an outer layer.
- `app/schemas.py` provides backward-compatible re-exports of all Pydantic models.
- The LLM provider interface lives in `domain/interfaces/`; concrete implementations live in `infrastructure/llm/`.
- Use-case service classes live in `application/use_cases/`.
- HTTP routing lives in `presentation/controllers/` as FastAPI `APIRouter` instances.

## Upcoming backend steps (from AGENTS.md)

- ~~Step 10: add `api/Dockerfile` for local containerization.~~ **Done**
- ~~Step 12: refactor backend structure to Onion Architecture.~~ **Done**
- Step 13: introduce LangGraph for orchestration of analysis/question/evaluation/report nodes.
- Step 14: add LangChain monitoring/observability hooks around LLM operations.
- Step 15: add pytest-based automated tests for MVP-critical backend flows.
- Step 16: add CI workflows to run backend tests and build Docker images.

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

Notes:

- Upload endpoint normalizes filename to `snake_case` before saving.
- Duplicate uploads for the same `interview_id + document_type` return `409`.

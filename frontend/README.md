# Frontend (React + TypeScript + Vite)

This directory contains the MVP frontend for the AI Interviewer Chatbot.

## Implemented scope

- Vite + React + TypeScript setup
- Routes for admin and candidate flows
- Simple top navigation
- API client configured via `VITE_API_URL`
- Admin form to create interview
- Redirect to `/admin/interviews/:id` after creation
- Interview selector dropdown on interview details page (titles from API)
- Resume and role-description PDF uploads on interview details page
- Upload status feedback with extracted character count + UI refresh on upload
- Friendlier error messages from backend `detail`
- Match Analysis section rendering structured LLM JSON output (`role_summary`, `candidate_summary`, `focus_areas`, `potential_gaps`)
- Candidate interview start flow with status-aware UI
- Candidate page validation for missing/invalid interview ids

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

The app will run on Vite's default local URL (usually `http://localhost:5173`).

## Routes

- `/admin`
- `/admin/interviews`
- `/admin/interviews/:id`
- `/interview`
- `/interview/:id`

## Admin flow (Step 4)

1. Open `/admin`.
2. Fill in:
   - Title
   - Target questions
   - Starting difficulty
3. Click **Create Interview**.
4. App calls `POST /interviews` and redirects to `/admin/interviews/:id`.

## Requirements for Step 4 test

- Backend API must be running at `VITE_API_URL` (default: `http://localhost:8000`).
- Backend must be configured with Supabase and schema from `docs/supabase_schema.sql` applied.

## Admin document upload and analysis flow (Step 5 & 6)

1. Create one or more interviews from `/admin`.
2. On `/admin/interviews/:id`, choose an interview in the dropdown.
3. Upload:
   - Resume PDF
   - Role Description PDF
4. Each upload replaces the previous document for that type.
5. UI refreshes to show the newly uploaded filename and character count.
6. Click **Run Match Analysis**.
7. App calls `POST /interviews/{selectedInterviewId}/analyze`.
8. UI renders structured LLM feedback (summaries, focus areas, and gaps).

Backend requirements:
- Supabase Storage bucket `interview-documents` must exist.
- `LLM_PROVIDER` must be valid (e.g. `mock` or valid credentials for `openai`, `gemini`, `deepseek`).

## Candidate start flow (Step 7)

1. Open `/interview/:id` with a real interview UUID.
2. Page loads interview status from `GET /interviews/{id}`.
3. If status is `READY`, click **Start Interview**.
4. Frontend calls `POST /interviews/{id}/start`.
5. On success, first question is displayed:
   - question content
   - topic
   - difficulty
   - expected signals
6. If status is `IN_PROGRESS`, page attempts to display latest assistant question.

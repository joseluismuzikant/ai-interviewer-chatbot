# Frontend (React + TypeScript + Vite)

This directory contains the MVP frontend for the AI Interviewer Chatbot.

## Implemented scope

- Vite + React + TypeScript setup
- Routes for admin and candidate flows
- API client configured via `VITE_API_URL`
- Reusable UI primitives for consistent layout and styling:
  - page container
  - card
  - section title
  - status badge
  - alert/message blocks
  - metric card
- Responsive global layout with sticky header/navigation and max-width content
- Admin interview creation form (title, target questions, starting difficulty)
- Interview Details page with sectioned workflow:
  - Setup
  - Documents
  - Match Analysis
  - Final Report
  - Transcript
- Document upload UI for resume and role description with current filename + extracted character count
- Match analysis rendering (`role_summary`, `candidate_summary`, `focus_areas`, `potential_gaps`)
- Candidate start flow (`POST /interviews/{id}/start`)
- Candidate answer flow (`POST /interviews/{id}/answer`) with progress and completion card
- Candidate UI intentionally hides internal evaluation data and expected signals
- Final report flow (`POST /interviews/{id}/report`, `GET /interviews/{id}/report`) with admin-side rendering
- Transcript rendering in chat-style bubbles on the admin page

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

The app runs on Vite's default local URL (usually `http://localhost:5173`).

## Routes

- `/admin`
- `/admin/interviews`
- `/admin/interviews/:id`
- `/interview`
- `/interview/:id`

## Admin flow

1. Open `/admin`.
2. Fill in title, target questions, and starting difficulty.
3. Click **Create Interview**.
4. App calls `POST /interviews` and redirects to `/admin/interviews/:id`.

## Interview Details flow (Steps 5-9)

1. Open `/admin/interviews/:id`.
2. Select interview from the dropdown in **Setup**.
3. Verify status badge and candidate interview link.
4. In **Documents**, upload:
   - Resume PDF
   - Role Description PDF
5. Click **Run Match Analysis** in **Match Analysis**.
6. Open candidate view and complete interview loop.
7. Return to **Final Report** and click **Generate Report** when status is `COMPLETED`.
8. Review report sections:
   - summary
   - overall score
   - strengths
   - weaknesses
   - integrity notes
   - recommendation + rationale
9. Inspect **Transcript** chat thread.

## Candidate flow (Steps 7-8)

1. Open `/interview/:id` with a real interview UUID.
2. Page loads interview and status from `GET /interviews/{id}`.
3. If status is `READY`, click **Start Interview**.
4. On success, current question renders with:
   - question content
   - topic
   - difficulty
   - progress (`Question X of Y`) when available
5. Submit answers from the textarea.
6. While submitting, UI shows:
   - `Evaluating answer and preparing next question...`
7. After completion, UI shows:
   - `Interview completed. Thank you for your responses.`

Not displayed to candidate (intentional for MVP):

- evaluation payload (`score`, `rationale`, `evidence`, `followup_hint`)
- expected signals

## UI and styling notes

- Plain CSS only (`src/styles.css`), no Tailwind or external UI framework.
- Design is intentionally simple and demo-ready:
  - neutral professional palette
  - clear section hierarchy
  - readable spacing and responsive cards
  - status and recommendation badges

## Backend requirements

- API must run at `VITE_API_URL` (default: `http://localhost:8000`).
- Supabase schema from `docs/supabase_schema.sql` must be applied.
- Supabase Storage bucket `interview-documents` must exist.
- `LLM_PROVIDER` must be configured (recommend `mock` for local MVP testing).

## Upcoming frontend steps (from AGENTS.md)

- ~~Step 10: add `frontend/Dockerfile` for local containerized runs.~~ **Done**
- Step 15: add automated frontend tests using Vitest + Testing Library.
- Step 16: add CI workflows to run frontend tests and build frontend Docker images.

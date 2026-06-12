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
- Upload status feedback with extracted character count
- Friendlier error messages from backend `detail`

## Run locally

```bash
npm install
cp .env.example .env
npm run dev
```

The app will run on Vite's default local URL (usually `http://localhost:5173`).

## Routes

- `/admin`
- `/admin/interviews/:id`
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

## Admin document upload flow (Step 5)

1. Create one or more interviews from `/admin`.
2. On `/admin/interviews/:id`, choose an interview in the dropdown.
3. Upload:
   - Resume PDF
   - Role Description PDF
4. Each upload calls `POST /interviews/{selectedInterviewId}/documents`.
5. UI shows status message with extracted character count.

Step 5 backend requirement: Supabase Storage bucket `interview-documents` must exist.

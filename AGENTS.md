# Visual OpenCode Instructions — AI Interviewer Chatbot MVP

Project path:

```bash
/home/luigi/workspace/projects/ITX/ai-interviewer-chatbot
```

## How to use this file

Use Visual OpenCode from inside the project folder.

Start by asking OpenCode to read this file and follow it step by step.

Suggested first prompt:

```text
Read this instruction file and implement only Step 1.
Do not jump ahead.
After finishing, summarize what you changed and which command I should run to verify it.
```

---

## Project goal

Build a local MVP for an AI Interviewer Chatbot.

The MVP must support this flow:

```text
Admin creates interview
→ Admin uploads resume and role description
→ API extracts text
→ LLM analyzes candidate-role match
→ Candidate starts interview
→ System asks questions
→ Candidate answers
→ LLM scores answers
→ System adjusts difficulty
→ System generates final report
```

---

## Tech decisions

Use this stack:

```text
Frontend: React + TypeScript + Vite
Backend: FastAPI + Python
Database: Supabase PostgreSQL
File storage: Supabase Storage
LLM: OpenAI API with a mini model
Initial development: local
Deployment later: DigitalOcean Droplet with Docker
```

Do not add authentication for the MVP.

Candidate access can be handled with an interview ID or token later.

---

## Repository structure

Use this structure:

```text
ai-interviewer-chatbot/
├── frontend/
├── api/
├── docs/
├── docker-compose.yml
├── README.md
└── AGENTS.md
```

---

## Rules for OpenCode

1. Work step by step.
2. Do not implement the full project in one pass.
3. Ask before changing the architecture.
4. Prefer simple MVP code over complex abstractions.
5. Keep the backend and frontend runnable locally.
6. Add clear README instructions when commands are introduced.
7. Do not commit secrets.
8. Do not create authentication unless explicitly requested.
9. Use environment variables for Supabase and OpenAI credentials.
10. After each step, explain:
    - files changed;
    - commands to run;
    - how to test manually.

---

# Step 1 — Create FastAPI skeleton

Create the initial backend structure:

```text
api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── llm.py
│   ├── interview_service.py
│   └── document_service.py
├── requirements.txt
├── .env.example
└── README.md
```

Requirements:

- Add FastAPI app.
- Add health endpoint:

```http
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

- Add CORS configuration for the local frontend.
- Add environment config loading from `.env`.
- Add `.env.example` with:

```env
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

Do not implement Supabase yet.

Validation command:

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then test:

```bash
curl http://localhost:8000/health
```

---

# Step 2 — Create React frontend skeleton

Create the frontend using Vite React TypeScript.

Requirements:

- Add routes:
  - `/admin`
  - `/admin/interviews/:id`
  - `/interview/:id`
- Add simple navigation.
- Add API client configured with:

```env
VITE_API_URL=http://localhost:8000
```

Initial pages:

```text
Admin page:
- title
- Create Interview button placeholder

Interview details page:
- title
- placeholder for upload and analysis

Candidate page:
- title
- placeholder for chat
```

Validation command:

```bash
cd frontend
npm install
npm run dev
```

---

# Step 3 — Supabase database setup

Add Supabase client in the backend.

Create SQL migration documentation under:

```text
docs/supabase_schema.sql
```

Initial tables:

```sql
create table interviews (
  id uuid primary key default gen_random_uuid(),
  status text not null default 'DRAFT',
  title text,
  target_questions int default 8,
  current_question_number int default 0,
  current_difficulty numeric default 5,
  match_analysis_json jsonb,
  report_json jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  interview_id uuid references interviews(id) on delete cascade,
  role text not null,
  content text not null,
  question_number int,
  difficulty_level numeric,
  answer_quality_score numeric,
  response_time_ms int,
  paste_detected boolean default false,
  created_at timestamptz default now()
);
```

Backend endpoints:

```http
POST /interviews
GET /interviews/{interview_id}
```

---

# Step 4 — Admin create interview from UI

Implement:

- Admin form to create an interview.
- Fields:
  - title
  - target questions
  - starting difficulty
- On submit, call backend.
- Redirect to `/admin/interviews/:id`.

Keep UI simple.

---

# Step 5 — Document upload

Backend endpoint:

```http
POST /interviews/{interview_id}/documents
```

Support two document types:

```text
resume
role_description
```

Requirements:

- Accept PDF files.
- Extract text with PyMuPDF.
- Store uploaded files in Supabase Storage.
- Store extracted text temporarily in backend/database as needed.
- Return extracted character count.

Frontend:

- Upload resume.
- Upload role description.
- Show upload status.

---

# Step 6 — LLM match analysis

Backend endpoint:

```http
POST /interviews/{interview_id}/analyze
```

Input:

- extracted resume text;
- extracted role description text.

Use OpenAI API.

Return strict JSON:

```json
{
  "role_summary": "string",
  "candidate_summary": "string",
  "focus_areas": [
    {
      "topic": "string",
      "reason": "string"
    }
  ],
  "potential_gaps": [
    {
      "topic": "string",
      "reason": "string"
    }
  ]
}
```

Persist the result in:

```text
interviews.match_analysis_json
```

Frontend:

- Add Analyze button.
- Display match analysis.

---

# Step 7 — Interview start

Backend endpoint:

```http
POST /interviews/{interview_id}/start
```

Behavior:

- Validate interview has match analysis.
- Set status to `IN_PROGRESS`.
- Generate first question using focus areas.
- Store assistant message in `messages`.
- Return first question.

Frontend candidate page:

- Load interview.
- Show Start Interview button.
- Display first question.

---

# Step 8 — Answer scoring and next question

Backend endpoint:

```http
POST /interviews/{interview_id}/answer
```

Request:

```json
{
  "answer": "string",
  "response_time_ms": 45000,
  "paste_detected": false
}
```

Behavior:

1. Store candidate answer.
2. Evaluate answer with LLM.
3. Return strict JSON evaluation:

```json
{
  "score": 7,
  "rationale": "string",
  "evidence": "string",
  "followup_hint": "string"
}
```

4. Update difficulty:

```text
if score >= 7 → difficulty += 0.5
if score <= 4 → difficulty -= 0.5
clamp between 3 and 10
```

5. Generate next question.
6. Stop after target question count.

Frontend:

- Textarea for answer.
- Detect paste event.
- Track response time.
- Submit answer.
- Show next question.

---

# Step 9 — Final report

Backend endpoint:

```http
POST /interviews/{interview_id}/report
GET /interviews/{interview_id}/report
```

Report JSON:

```json
{
  "summary": "string",
  "overall_score": 7.2,
  "strengths": ["string"],
  "weaknesses": ["string"],
  "integrity_notes": ["string"],
  "recommendation": "YES | MIXED | NO",
  "recommendation_rationale": "string"
}
```

Frontend admin page:

- Show final report.
- Show transcript.
- Show score per answer.

---

# Step 10 — Dockerize locally

Add:

- `api/Dockerfile`
- `frontend/Dockerfile`
- root `docker-compose.yml`

For local MVP:

```text
frontend → localhost:3000
api      → localhost:8000
```

Supabase remains managed externally.

---

# Step 11 — Prepare Droplet deployment later

Do not deploy until local MVP works.

Later deployment will use:

```text
GitHub Actions
→ build Docker images
→ push to GitHub Container Registry
→ SSH into Droplet
→ docker compose pull
→ docker compose up -d
```

Do not implement deployment until the local MVP is complete.

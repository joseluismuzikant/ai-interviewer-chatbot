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
→ load resume extracted_text from documents
→ load role_description extracted_text from documents
→ validate both exist
→ call OpenAI
→ store result in interviews.match_analysis_json
→ update status to READY
400 if resume is missing
400 if role_description is missing
400 if extracted text is empty
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

In the Interview Details page, improve the document upload behavior.

Requirements:

1. For each document type, show the latest uploaded document filename:
   - resume
   - role_description

2. When the page loads, call GET /interviews/{interview_id}/documents and display the current uploaded document metadata.

3. When the user uploads a new document for an existing document type:
   - replace the previous document of that same type;
   - delete or overwrite the previous record/file if the backend already supports it;
   - if the backend does not support deletion yet, update the upload endpoint to behave as an upsert by interview_id + document_type.

4. After upload succeeds:
   - refresh the document list;
   - show the new filename;
   - show extracted_character_count;
   - show a success message.

5. Keep the implementation simple for the MVP.

Do not change the overall architecture.
Do not add authentication.+-9`+

Do not start Step 7 yet.

---

# Step 7 — Interview start


Context:
The project is an AI Interviewer Chatbot MVP.
The current flow already works up to:
- create interview
- upload resume
- upload role description
- extract PDF text
- store documents
- analyze resume + role description with the configured LLM provider
- store match_analysis_json
- update interview status to READY

Now I need the candidate interview start flow.

Requirements:

1. Add backend endpoint:

POST /interviews/{interview_id}/start

2. Backend behavior:

- Load the interview by id.
- Return 404 if the interview does not exist.
- Only allow starting when interview.status = READY.
- If interview.status = IN_PROGRESS, do not generate a duplicate first question.
  Instead, return the latest assistant question for that interview.
- Return 400 if the interview status is not READY or IN_PROGRESS.
- Validate that match_analysis_json exists.
- Validate that match_analysis_json has focus_areas.
- Generate the first interview question using focus_areas from match_analysis_json.
- Use interview.current_difficulty as the first question difficulty.
- Use the existing LLM provider abstraction so it works with:
  - mock
  - openai
  - gemini
  - deepseek

3. Add LLM provider method:

generate_question(context: dict) -> dict

The context should include:
- focus_areas
- potential_gaps if available
- current_difficulty
- question_number = 1
- previous_messages = empty list for Step 7

4. The LLM response must be strict JSON:

{
  "question": "string",
  "topic": "string",
  "difficulty": 5,
  "expected_signals": ["string"]
}

5. Add Pydantic schema validation for the generated question.

If the provider returns invalid JSON or invalid schema, return HTTP 503 with this message:

"LLM returned invalid question JSON."

6. Add mock provider support.

The mock provider should return a valid fixed first question like:

{
  "question": "Can you describe how you would design a scalable REST API for a financial services application?",
  "topic": "Backend API design",
  "difficulty": 5,
  "expected_signals": [
    "API resource design",
    "validation and error handling",
    "security considerations",
    "database transaction boundaries",
    "observability"
  ]
}

7. Store the generated first question in the messages table as an assistant message:

- interview_id = current interview id
- role = assistant
- content = generated question text
- question_number = 1
- difficulty_level = interview.current_difficulty
- answer_quality_score = null
- response_time_ms = null
- paste_detected = false

8. Update the interview row:

- status = IN_PROGRESS
- current_question_number = 1

9. Return a response like:

{
  "interview_id": "uuid",
  "status": "IN_PROGRESS",
  "question": {
    "id": "message uuid if available",
    "content": "question text",
    "topic": "Backend API design",
    "difficulty": 5,
    "question_number": 1,
    "expected_signals": ["string"]
  }
}

If returning the message id is difficult with the current Supabase insert, return everything else and keep id optional.

10. Add API client method in the frontend:

startInterview(interviewId)

It should call:

POST /interviews/{interview_id}/start

11. Update the Candidate Interview page:

- Load the interview by id from the URL.
- Show interview status.
- If status is READY, show a Start Interview button.
- When Start Interview is clicked:
  - call startInterview(interviewId)
  - show loading state
  - display any error clearly
  - display the first question on success
- If status is IN_PROGRESS, show the latest assistant question if it is available.
- Display:
  - question text
  - topic
  - difficulty
  - expected signals

12. Add or update a backend endpoint if needed to fetch messages for an interview.

Preferred endpoint:

GET /interviews/{interview_id}/messages

It should return messages ordered by created_at ascending.

13. Do not implement answer submission.
14. Do not implement answer scoring.
15. Do not implement adaptive difficulty yet.
16. Do not implement final report yet.
17. Do not add authentication.
18. Do not change the existing architecture.
19. Keep the implementation simple and MVP-focused.

After finishing, tell me:

- files changed
- how to test with Postman
- how to test from the frontend
- expected request/response examples
- any assumptions you made


---

# Step 8 — Answer scoring and next question

Backend endpoint:

```http
POST /interviews/{interview_id}/answer

→ store answer
→ score answer
→ update difficulty
→ generate next question
→ store next question
- Important: stop after target_questions.
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

Backend endpoints:

```http
POST /interviews/{interview_id}/report
GET /interviews/{interview_id}/report
```
The report should use:
messages
scores
telemetry
match_analysis_json

POST store it in:
interviews.report_json
and update status to: COMPLETED

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

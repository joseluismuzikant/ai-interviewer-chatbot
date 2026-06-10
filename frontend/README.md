# Frontend (React + TypeScript + Vite)

This directory contains the MVP frontend for the AI Interviewer Chatbot.

## Step 2 scope

- Vite + React + TypeScript setup
- Routes for admin and candidate flows
- Simple top navigation
- API client configured via `VITE_API_URL`

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

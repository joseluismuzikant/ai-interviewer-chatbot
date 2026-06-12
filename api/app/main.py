from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.interview_service import InterviewService
from app.schemas import HealthResponse, InterviewCreateRequest, InterviewResponse
from app.supabase_client import get_supabase_client

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


def get_interview_service() -> InterviewService:
    settings = get_settings()
    try:
        supabase = get_supabase_client(settings)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return InterviewService(supabase=supabase)


@app.post("/interviews", response_model=InterviewResponse)
def create_interview(
    payload: InterviewCreateRequest,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.create_interview(payload)
    return InterviewResponse(**interview)


@app.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.get_interview(interview_id)
    return InterviewResponse(**interview)

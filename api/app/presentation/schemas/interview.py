from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InterviewCreateRequest(BaseModel):
    title: str | None = None
    target_questions: int = Field(default=8, ge=1, le=30)
    starting_difficulty: float = Field(default=5, ge=3, le=10)


class InterviewResponse(BaseModel):
    id: UUID
    status: str
    title: str | None = None
    target_questions: int
    current_question_number: int
    current_difficulty: float
    match_analysis_json: dict | None = None
    report_json: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

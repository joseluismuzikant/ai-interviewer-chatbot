from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr


class HealthResponse(BaseModel):
    status: str


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


class FocusArea(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: StrictStr
    reason: StrictStr


class PotentialGap(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: StrictStr
    reason: StrictStr


class MatchAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_summary: StrictStr
    candidate_summary: StrictStr
    focus_areas: list[FocusArea]
    potential_gaps: list[PotentialGap]


class InterviewQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: StrictStr
    topic: StrictStr
    difficulty: StrictInt | StrictFloat
    expected_signals: list[StrictStr]


class StartedQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID | None = None
    content: StrictStr
    topic: StrictStr
    difficulty: float
    question_number: int
    expected_signals: list[StrictStr]


class InterviewStartResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interview_id: UUID
    status: Literal["IN_PROGRESS"]
    question: StartedQuestion


class DocumentUploadResponse(BaseModel):
    interview_id: UUID
    document_type: Literal["resume", "role_description"]
    extracted_character_count: int
    storage_path: str


class DocumentRecord(BaseModel):
    id: UUID
    interview_id: UUID
    document_type: Literal["resume", "role_description"]
    filename: str
    storage_path: str
    mime_type: str | None = None
    extracted_text: str | None = None
    extracted_character_count: int
    created_at: datetime | None = None


class DocumentListResponse(BaseModel):
    interview_id: UUID
    documents: list[DocumentRecord]


class DocumentStorageListResponse(BaseModel):
    interview_id: UUID
    documents: list[str]


class DocumentDeleteResponse(BaseModel):
    interview_id: UUID
    filename: str
    deleted: bool


class MessageResponse(BaseModel):
    id: UUID
    interview_id: UUID
    role: Literal["assistant", "candidate", "system"]
    content: str
    question_number: int | None = None
    difficulty_level: float | None = None
    answer_quality_score: float | None = None
    response_time_ms: int | None = None
    paste_detected: bool | None = None
    created_at: datetime | None = None

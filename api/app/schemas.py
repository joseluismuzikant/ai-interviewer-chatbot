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


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: StrictStr = Field(min_length=1)
    response_time_ms: StrictInt = Field(ge=0)
    paste_detected: bool


class AnswerEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: StrictInt = Field(ge=1, le=10)
    rationale: StrictStr = Field(min_length=1)
    evidence: StrictStr = Field(min_length=1)
    followup_hint: StrictStr = Field(min_length=1)


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


class InterviewAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interview_id: UUID
    status: Literal["IN_PROGRESS", "COMPLETED"]
    evaluation: AnswerEvaluation
    next_question: StartedQuestion | None = None


class GeneratedReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: StrictStr = Field(min_length=1)
    strengths: list[StrictStr]
    weaknesses: list[StrictStr]
    recommendation: Literal["YES", "MIXED", "NO"]
    recommendation_rationale: StrictStr = Field(min_length=1)


class FinalReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: StrictStr = Field(min_length=1)
    overall_score: float = Field(ge=0, le=10)
    strengths: list[StrictStr]
    weaknesses: list[StrictStr]
    integrity_notes: list[StrictStr]
    recommendation: Literal["YES", "MIXED", "NO"]
    recommendation_rationale: StrictStr = Field(min_length=1)


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

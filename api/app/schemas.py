from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


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

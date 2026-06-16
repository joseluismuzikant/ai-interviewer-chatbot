from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


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

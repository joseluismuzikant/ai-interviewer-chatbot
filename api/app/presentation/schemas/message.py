from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


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

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from app.presentation.schemas.question import StartedQuestion


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


class InterviewAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    interview_id: UUID
    status: Literal["IN_PROGRESS", "COMPLETED"]
    evaluation: AnswerEvaluation
    next_question: StartedQuestion | None = None

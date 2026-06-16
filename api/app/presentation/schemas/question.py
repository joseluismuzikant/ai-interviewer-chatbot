from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StrictFloat, StrictInt, StrictStr


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

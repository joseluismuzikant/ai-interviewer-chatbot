from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr


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

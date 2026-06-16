from pydantic import BaseModel, ConfigDict, StrictStr


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

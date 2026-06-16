from uuid import UUID

from fastapi import HTTPException
from pydantic import ValidationError
from supabase import Client

from app.providers.base import LLMProvider
from app.schemas import FinalReportResponse, GeneratedReport


class ReportService:
    _MIN_ANSWER_LENGTH_FOR_SPEED_CHECK = 80
    _VERY_FAST_MS_PER_CHAR_THRESHOLD = 20.0

    def __init__(self, supabase: Client, llm: LLMProvider) -> None:
        self.supabase = supabase
        self.llm = llm

    def generate_report(self, interview: dict) -> FinalReportResponse:
        interview_id_value = interview.get("id")
        if not interview_id_value:
            raise HTTPException(status_code=500, detail="Invalid interview data")

        interview_id = UUID(str(interview_id_value))

        status = str(interview.get("status") or "")
        if status != "COMPLETED":
            raise HTTPException(
                status_code=400,
                detail="Interview must be COMPLETED before generating a report.",
            )

        match_analysis = interview.get("match_analysis_json")
        if not isinstance(match_analysis, dict):
            raise HTTPException(status_code=400, detail="match_analysis_json is missing.")

        transcript = self._list_messages(interview_id)
        candidate_messages = [
            message
            for message in transcript
            if message.get("role") == "candidate"
        ]
        candidate_scored_messages = [
            message
            for message in candidate_messages
            if message.get("answer_quality_score") is not None
        ]
        if not candidate_scored_messages:
            raise HTTPException(
                status_code=400,
                detail="No scored candidate answers found for this interview.",
            )

        overall_score = self._calculate_overall_score(candidate_scored_messages)
        integrity_notes = self._build_integrity_notes(candidate_messages)

        report_context = {
            "match_analysis_json": match_analysis,
            "ordered_transcript_messages": transcript,
            "overall_score": overall_score,
            "integrity_notes": integrity_notes,
            "target_questions": int(interview.get("target_questions") or 0),
            "current_question_number": int(interview.get("current_question_number") or 0),
        }

        try:
            report_llm_raw = self.llm.generate_report(report_context)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        try:
            report_llm = GeneratedReport.model_validate(report_llm_raw)
        except ValidationError as exc:
            raise HTTPException(
                status_code=503,
                detail="LLM returned invalid report JSON.",
            ) from exc

        final_report = FinalReportResponse(
            summary=report_llm.summary,
            overall_score=overall_score,
            strengths=report_llm.strengths,
            weaknesses=report_llm.weaknesses,
            integrity_notes=integrity_notes,
            recommendation=report_llm.recommendation,
            recommendation_rationale=report_llm.recommendation_rationale,
        )

        try:
            self.supabase.table("interviews").update(
                {"report_json": final_report.model_dump()}
            ).eq("id", str(interview_id)).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not persist final report.",
            ) from exc

        return final_report

    def get_report(self, interview: dict) -> FinalReportResponse:
        report_json = interview.get("report_json")
        if not isinstance(report_json, dict):
            raise HTTPException(status_code=404, detail="Report not generated yet.")

        try:
            return FinalReportResponse.model_validate(report_json)
        except ValidationError as exc:
            raise HTTPException(
                status_code=500,
                detail="Stored report JSON is invalid.",
            ) from exc

    def _list_messages(self, interview_id: UUID) -> list[dict]:
        response = (
            self.supabase.table("messages")
            .select(
                "id,role,content,question_number,difficulty_level,"
                "answer_quality_score,response_time_ms,paste_detected,created_at"
            )
            .eq("interview_id", str(interview_id))
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []

    @staticmethod
    def _calculate_overall_score(candidate_scored_messages: list[dict]) -> float:
        scores = [
            float(message["answer_quality_score"])
            for message in candidate_scored_messages
            if message.get("answer_quality_score") is not None
        ]
        if not scores:
            raise HTTPException(
                status_code=400,
                detail="No scored candidate answers found for this interview.",
            )
        return round(sum(scores) / len(scores), 1)

    def _build_integrity_notes(self, candidate_messages: list[dict]) -> list[str]:
        notes: list[str] = []

        has_paste_event = any(
            bool(message.get("paste_detected")) for message in candidate_messages
        )
        if has_paste_event:
            notes.append("Paste events were detected during the interview.")

        has_very_fast_answer = any(
            self._is_very_fast_for_length(message)
            for message in candidate_messages
        )
        if has_very_fast_answer:
            notes.append(
                "Some answers were submitted very quickly relative to their length."
            )

        return notes

    def _is_very_fast_for_length(self, message: dict) -> bool:
        content = str(message.get("content") or "").strip()
        if len(content) < self._MIN_ANSWER_LENGTH_FOR_SPEED_CHECK:
            return False

        response_time_ms = message.get("response_time_ms")
        if response_time_ms is None:
            return False

        try:
            response_time_ms_value = float(response_time_ms)
        except (TypeError, ValueError):
            return False

        if response_time_ms_value <= 0:
            return True

        milliseconds_per_character = response_time_ms_value / len(content)
        return (
            milliseconds_per_character
            < self._VERY_FAST_MS_PER_CHAR_THRESHOLD
        )

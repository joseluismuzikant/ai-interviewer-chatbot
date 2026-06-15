from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.providers.base import LLMProvider
from app.schemas import InterviewStartResponse, StartedQuestion


class InterviewStartService:
    def __init__(self, supabase: Client, llm: LLMProvider) -> None:
        self.supabase = supabase
        self.llm = llm
        self._question_meta_cache: dict[str, dict] = {}

    def start_interview(self, interview: dict) -> InterviewStartResponse:
        interview_id = interview.get("id")
        if not interview_id:
            raise HTTPException(status_code=500, detail="Invalid interview data")

        interview_status = interview.get("status")
        if interview_status not in {"READY", "IN_PROGRESS"}:
            raise HTTPException(
                status_code=400,
                detail="Interview can only be started from READY or IN_PROGRESS status.",
            )

        match_analysis = interview.get("match_analysis_json")
        if not isinstance(match_analysis, dict):
            raise HTTPException(
                status_code=400,
                detail="match_analysis_json is missing.",
            )

        focus_areas = match_analysis.get("focus_areas")
        if not isinstance(focus_areas, list) or len(focus_areas) == 0:
            raise HTTPException(
                status_code=400,
                detail="match_analysis_json.focus_areas is missing or empty.",
            )

        if interview_status == "IN_PROGRESS":
            latest_assistant = self._get_latest_assistant_message(UUID(str(interview_id)))
            if not latest_assistant:
                raise HTTPException(
                    status_code=400,
                    detail="Interview is IN_PROGRESS but no assistant question was found.",
                )
            return self._build_response_from_existing_message(
                interview_id=UUID(str(interview_id)),
                latest_assistant=latest_assistant,
            )

        current_difficulty = float(interview.get("current_difficulty", 5))
        context = {
            "focus_areas": focus_areas,
            "potential_gaps": match_analysis.get("potential_gaps") or [],
            "current_difficulty": current_difficulty,
            "question_number": 1,
            "previous_messages": [],
        }

        try:
            generated_question = self.llm.generate_question(context)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        message_payload = {
            "interview_id": str(interview_id),
            "role": "assistant",
            "content": generated_question["question"],
            "question_number": 1,
            "difficulty_level": current_difficulty,
            "answer_quality_score": None,
            "response_time_ms": None,
            "paste_detected": False,
        }

        try:
            message_insert = self.supabase.table("messages").insert(message_payload).execute()
            inserted_messages = message_insert.data or []
            inserted_message = inserted_messages[0] if inserted_messages else None
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not store first interview question.",
            ) from exc

        try:
            self.supabase.table("interviews").update(
                {
                    "status": "IN_PROGRESS",
                    "current_question_number": 1,
                }
            ).eq("id", str(interview_id)).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not update interview status.",
            ) from exc

        self._question_meta_cache[str(interview_id)] = {
            "topic": generated_question["topic"],
            "difficulty": current_difficulty,
            "expected_signals": generated_question["expected_signals"],
        }

        question = StartedQuestion(
            id=UUID(inserted_message["id"]) if isinstance(inserted_message, dict) and inserted_message.get("id") else None,
            content=generated_question["question"],
            topic=generated_question["topic"],
            difficulty=current_difficulty,
            question_number=1,
            expected_signals=generated_question["expected_signals"],
        )
        return InterviewStartResponse(
            interview_id=UUID(str(interview_id)),
            status="IN_PROGRESS",
            question=question,
        )

    def _get_latest_assistant_message(self, interview_id: UUID) -> dict | None:
        response = (
            self.supabase.table("messages")
            .select("id,content,question_number,difficulty_level")
            .eq("interview_id", str(interview_id))
            .eq("role", "assistant")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        data = response.data or []
        if not data:
            return None
        return data[0] if isinstance(data[0], dict) else None

    def _build_response_from_existing_message(
        self,
        interview_id: UUID,
        latest_assistant: dict,
    ) -> InterviewStartResponse:
        cached_meta = self._question_meta_cache.get(str(interview_id), {})
        difficulty_level = latest_assistant.get("difficulty_level")
        question = StartedQuestion(
            id=UUID(latest_assistant["id"]) if latest_assistant.get("id") else None,
            content=str(latest_assistant.get("content", "")),
            topic=str(cached_meta.get("topic", "Unknown topic")),
            difficulty=float(
                difficulty_level
                if difficulty_level is not None
                else cached_meta.get("difficulty", 0)
            ),
            question_number=int(latest_assistant.get("question_number") or 1),
            expected_signals=list(cached_meta.get("expected_signals", [])),
        )
        return InterviewStartResponse(
            interview_id=interview_id,
            status="IN_PROGRESS",
            question=question,
        )

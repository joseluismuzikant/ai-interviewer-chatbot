from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.application.use_cases.question_meta_store import get_question_meta, set_question_meta
from app.domain.interfaces.llm_provider import LLMProvider
from app.presentation.schemas.answer import AnswerEvaluation, AnswerRequest, InterviewAnswerResponse
from app.presentation.schemas.question import StartedQuestion


class InterviewAnswerService:
    def __init__(self, supabase: Client, llm: LLMProvider) -> None:
        self.supabase = supabase
        self.llm = llm

    def submit_answer(
        self,
        interview: dict,
        payload: AnswerRequest,
    ) -> InterviewAnswerResponse:
        interview_id_value = interview.get("id")
        if not interview_id_value:
            raise HTTPException(status_code=500, detail="Invalid interview data")

        interview_id = UUID(str(interview_id_value))
        status = str(interview.get("status") or "")
        if status != "IN_PROGRESS":
            raise HTTPException(
                status_code=400,
                detail="Interview must be IN_PROGRESS to submit an answer.",
            )

        if not payload.answer.strip():
            raise HTTPException(status_code=400, detail="Answer cannot be empty.")

        latest_assistant = self._get_latest_assistant_message(interview_id)
        if not latest_assistant:
            raise HTTPException(
                status_code=400,
                detail="No assistant question found to answer.",
            )

        latest_question_number = int(latest_assistant.get("question_number") or 1)
        latest_difficulty_level = float(latest_assistant.get("difficulty_level") or 5)

        candidate_message_payload = {
            "interview_id": str(interview_id),
            "role": "candidate",
            "content": payload.answer,
            "question_number": latest_question_number,
            "difficulty_level": latest_difficulty_level,
            "response_time_ms": payload.response_time_ms,
            "paste_detected": payload.paste_detected,
        }

        try:
            insert_result = self.supabase.table("messages").insert(candidate_message_payload).execute()
            inserted = insert_result.data or []
            candidate_message = inserted[0] if inserted else None
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not store candidate answer.",
            ) from exc

        match_analysis = interview.get("match_analysis_json")
        if not isinstance(match_analysis, dict):
            raise HTTPException(status_code=400, detail="match_analysis_json is missing.")

        focus_areas = match_analysis.get("focus_areas")
        if not isinstance(focus_areas, list) or len(focus_areas) == 0:
            raise HTTPException(
                status_code=400,
                detail="match_analysis_json.focus_areas is missing or empty.",
            )

        question_meta = get_question_meta(str(interview_id), latest_question_number) or {}

        previous_messages = self._list_messages(interview_id)
        eval_context = {
            "current_question": str(latest_assistant.get("content") or ""),
            "candidate_answer": payload.answer,
            "question_number": latest_question_number,
            "difficulty_level": latest_difficulty_level,
            "topic": question_meta.get("topic"),
            "expected_signals": question_meta.get("expected_signals") or [],
            "focus_areas": focus_areas,
            "previous_messages": previous_messages,
        }

        try:
            evaluation_raw = self.llm.evaluate_answer(eval_context)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        evaluation = AnswerEvaluation(**evaluation_raw)

        if isinstance(candidate_message, dict) and candidate_message.get("id"):
            try:
                self.supabase.table("messages").update(
                    {"answer_quality_score": evaluation.score}
                ).eq("id", candidate_message["id"]).execute()
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail="Could not update candidate answer score.",
                ) from exc

        current_difficulty = float(interview.get("current_difficulty") or 5)
        updated_difficulty = self._adjust_difficulty(current_difficulty, evaluation.score)

        current_question_number = int(interview.get("current_question_number") or latest_question_number)
        target_questions = int(interview.get("target_questions") or 8)

        if current_question_number >= target_questions:
            try:
                self.supabase.table("interviews").update(
                    {
                        "status": "COMPLETED",
                        "current_difficulty": updated_difficulty,
                    }
                ).eq("id", str(interview_id)).execute()
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail="Could not complete interview.",
                ) from exc

            return InterviewAnswerResponse(
                interview_id=interview_id,
                status="COMPLETED",
                evaluation=evaluation,
                next_question=None,
            )

        next_question_number = current_question_number + 1
        question_context = {
            "focus_areas": focus_areas,
            "potential_gaps": match_analysis.get("potential_gaps") or [],
            "previous_messages": previous_messages,
            "latest_evaluation": evaluation.model_dump(),
            "current_difficulty": updated_difficulty,
            "question_number": next_question_number,
        }

        try:
            next_question = self.llm.generate_question(question_context)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        assistant_message_payload = {
            "interview_id": str(interview_id),
            "role": "assistant",
            "content": next_question["question"],
            "question_number": next_question_number,
            "difficulty_level": updated_difficulty,
            "answer_quality_score": None,
            "response_time_ms": None,
            "paste_detected": False,
        }

        try:
            message_result = self.supabase.table("messages").insert(assistant_message_payload).execute()
            inserted_messages = message_result.data or []
            next_assistant = inserted_messages[0] if inserted_messages else None
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not store next assistant question.",
            ) from exc

        try:
            self.supabase.table("interviews").update(
                {
                    "current_question_number": next_question_number,
                    "current_difficulty": updated_difficulty,
                    "status": "IN_PROGRESS",
                }
            ).eq("id", str(interview_id)).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not update interview progress.",
            ) from exc

        set_question_meta(
            str(interview_id),
            next_question_number,
            {
                "topic": next_question["topic"],
                "difficulty": updated_difficulty,
                "expected_signals": next_question["expected_signals"],
            },
        )

        next_question_response = StartedQuestion(
            id=UUID(next_assistant["id"]) if isinstance(next_assistant, dict) and next_assistant.get("id") else None,
            content=next_question["question"],
            topic=next_question["topic"],
            difficulty=updated_difficulty,
            question_number=next_question_number,
            expected_signals=next_question["expected_signals"],
        )

        return InterviewAnswerResponse(
            interview_id=interview_id,
            status="IN_PROGRESS",
            evaluation=evaluation,
            next_question=next_question_response,
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
    def _adjust_difficulty(current: float, score: int) -> float:
        updated = current
        if score >= 7:
            updated += 0.5
        elif score <= 4:
            updated -= 0.5
        return max(3.0, min(10.0, updated))

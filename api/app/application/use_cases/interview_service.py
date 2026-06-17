from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.presentation.schemas.interview import InterviewCreateRequest


class InterviewService:
    def __init__(self, supabase: Client) -> None:
        self.supabase = supabase

    def list_interviews(self) -> list[dict]:
        response = self.supabase.table("interviews").select("*").execute()
        return response.data or []

    def create_interview(self, payload: InterviewCreateRequest) -> dict:
        insert_payload = {
            "title": payload.title,
            "target_questions": payload.target_questions,
            "current_difficulty": payload.starting_difficulty,
        }

        response = self.supabase.table("interviews").insert(insert_payload).execute()
        data = response.data or []
        if not data:
            raise HTTPException(status_code=500, detail="Could not create interview")

        return data[0]

    def get_interview(self, interview_id: UUID) -> dict:
        response = (
            self.supabase.table("interviews")
            .select("*")
            .eq("id", str(interview_id))
            .limit(1)
            .execute()
        )
        data = response.data or []
        if not data:
            raise HTTPException(status_code=404, detail="Interview not found")

        return data[0]

    def delete_interview(self, interview_id: UUID) -> None:
        self.get_interview(interview_id)
        interview_id_str = str(interview_id)
        for table in ("messages", "documents", "interviews"):
            self.supabase.table(table).delete().eq("interview_id" if table != "interviews" else "id", interview_id_str).execute()

    def list_messages(self, interview_id: UUID) -> list[dict]:
        response = (
            self.supabase.table("messages")
            .select(
                "id,interview_id,role,content,question_number,difficulty_level,"
                "answer_quality_score,response_time_ms,paste_detected,created_at"
            )
            .eq("interview_id", str(interview_id))
            .order("created_at", desc=False)
            .execute()
        )
        return response.data or []

from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.schemas import InterviewCreateRequest


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
        self.supabase.table("interviews").delete().eq("id", str(interview_id)).execute()

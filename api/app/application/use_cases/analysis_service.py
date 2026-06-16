from uuid import UUID

from fastapi import HTTPException
from supabase import Client

from app.domain.interfaces.llm_provider import LLMProvider


class AnalysisService:
    def __init__(self, supabase: Client, llm: LLMProvider) -> None:
        self.supabase = supabase
        self.llm = llm

    def analyze_interview(self, interview_id: UUID) -> dict:
        def fetch_document_text(doc_type: str) -> str:
            response = (
                self.supabase.table("documents")
                .select("extracted_text")
                .eq("interview_id", str(interview_id))
                .eq("document_type", doc_type)
                .limit(1)
                .execute()
            )
            data = response.data or []
            if not data:
                raise HTTPException(
                    status_code=400,
                    detail=f"{doc_type} document not found",
                )
            text = None
            if isinstance(data[0], dict):
                text = data[0].get("extracted_text")
            if not text or not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"{doc_type} extracted text is empty",
                )
            return text

        resume_text = fetch_document_text("resume")
        role_description_text = fetch_document_text("role_description")

        try:
            analysis = self.llm.analyze_match(resume_text, role_description_text)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc),
            ) from exc

        try:
            self.supabase.table("interviews").update(
                {
                    "match_analysis_json": analysis,
                    "status": "READY",
                }
            ).eq("id", str(interview_id)).execute()
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail="Could not persist match analysis",
            ) from exc

        return analysis

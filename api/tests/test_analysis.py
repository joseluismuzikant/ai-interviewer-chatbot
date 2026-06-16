import pytest

from tests.conftest import FAKE_SUPABASE
from app.application.use_cases.document_service import DocumentService


def _create_ready_interview(client):
    """Create an interview ready for analysis using the fake Supabase in-memory store."""
    from uuid import uuid4
    interview_id = str(uuid4())
    FAKE_SUPABASE._tables["interviews"].append({
        "id": interview_id,
        "status": "DRAFT",
        "title": "Analysis Test",
        "target_questions": 8,
        "current_question_number": 0,
        "current_difficulty": 5.0,
        "match_analysis_json": None,
        "report_json": None,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
    })
    FAKE_SUPABASE._tables["documents"].append({
        "id": str(uuid4()),
        "interview_id": interview_id,
        "document_type": "resume",
        "extracted_text": "Experienced Python developer with 5 years of backend experience.",
        "filename": "resume.pdf",
        "storage_path": f"{interview_id}/resume/resume.pdf",
        "mime_type": "application/pdf",
        "extracted_character_count": 55,
        "created_at": "2025-01-01T00:00:00",
    })
    FAKE_SUPABASE._tables["documents"].append({
        "id": str(uuid4()),
        "interview_id": interview_id,
        "document_type": "role_description",
        "extracted_text": "Senior Backend Engineer role requiring Python and cloud expertise.",
        "filename": "role.pdf",
        "storage_path": f"{interview_id}/role_description/role.pdf",
        "mime_type": "application/pdf",
        "extracted_character_count": 62,
        "created_at": "2025-01-01T00:00:00",
    })
    return interview_id


class TestAnalyzeInterview:
    def test_analyze_returns_match_analysis(self, client):
        interview_id = _create_ready_interview(client)
        resp = client.post(f"/interviews/{interview_id}/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert "role_summary" in data
        assert "candidate_summary" in data
        assert "focus_areas" in data
        assert "potential_gaps" in data
        assert isinstance(data["focus_areas"], list)
        assert isinstance(data["potential_gaps"], list)

    def test_analyze_updates_status_to_ready(self, client):
        interview_id = _create_ready_interview(client)
        client.post(f"/interviews/{interview_id}/analyze")
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["status"] == "READY"
        assert interview["match_analysis_json"] is not None

    def test_analyze_missing_document_returns_400(self, client):
        from uuid import uuid4
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "DRAFT",
            "title": "Missing Doc",
            "target_questions": 8,
            "current_question_number": 0,
            "current_difficulty": 5.0,
            "match_analysis_json": None,
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.post(f"/interviews/{interview_id}/analyze")
        assert resp.status_code == 400

    def test_analyze_nonexistent_interview(self, client):
        from uuid import uuid4
        resp = client.post(f"/interviews/{uuid4()}/analyze")
        assert resp.status_code == 404

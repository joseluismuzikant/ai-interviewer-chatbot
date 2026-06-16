import pytest

from tests.conftest import FAKE_SUPABASE
from app.application.use_cases.question_meta_store import set_question_meta
from uuid import uuid4


def _make_completed_interview() -> str:
    uid = str(uuid4())
    FAKE_SUPABASE._tables["interviews"].append({
        "id": uid,
        "status": "COMPLETED",
        "title": "Report Test",
        "target_questions": 2,
        "current_question_number": 2,
        "current_difficulty": 5.5,
        "match_analysis_json": {
            "role_summary": "A role",
            "candidate_summary": "A candidate",
            "focus_areas": [{"topic": "Python", "reason": "Core"}],
            "potential_gaps": [{"topic": "Cloud", "reason": "Limited"}],
        },
        "report_json": None,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
    })
    FAKE_SUPABASE._tables["messages"].append({
        "id": str(uuid4()),
        "interview_id": uid,
        "role": "assistant",
        "content": "Question 1?",
        "question_number": 1,
        "difficulty_level": 5.0,
        "answer_quality_score": None,
        "response_time_ms": None,
        "paste_detected": False,
        "created_at": "2025-01-01T00:01:00",
    })
    FAKE_SUPABASE._tables["messages"].append({
        "id": str(uuid4()),
        "interview_id": uid,
        "role": "candidate",
        "content": "Answer 1",
        "question_number": 1,
        "difficulty_level": 5.0,
        "answer_quality_score": 7,
        "response_time_ms": 45000,
        "paste_detected": False,
        "created_at": "2025-01-01T00:02:00",
    })
    FAKE_SUPABASE._tables["messages"].append({
        "id": str(uuid4()),
        "interview_id": uid,
        "role": "assistant",
        "content": "Question 2?",
        "question_number": 2,
        "difficulty_level": 5.5,
        "answer_quality_score": None,
        "response_time_ms": None,
        "paste_detected": False,
        "created_at": "2025-01-01T00:03:00",
    })
    FAKE_SUPABASE._tables["messages"].append({
        "id": str(uuid4()),
        "interview_id": uid,
        "role": "candidate",
        "content": "Answer 2",
        "question_number": 2,
        "difficulty_level": 5.5,
        "answer_quality_score": 8,
        "response_time_ms": 50000,
        "paste_detected": False,
        "created_at": "2025-01-01T00:04:00",
    })
    return uid


class TestGenerateReport:
    def test_generates_report(self, client):
        interview_id = _make_completed_interview()
        resp = client.post(f"/interviews/{interview_id}/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["summary"]
        assert data["overall_score"] == 7.5
        assert isinstance(data["strengths"], list)
        assert isinstance(data["weaknesses"], list)
        assert isinstance(data["integrity_notes"], list)
        assert data["recommendation"] in ("YES", "MIXED", "NO")
        assert data["recommendation_rationale"]

    def test_persists_report_json(self, client):
        interview_id = _make_completed_interview()
        client.post(f"/interviews/{interview_id}/report")
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["report_json"] is not None
        assert interview["report_json"]["overall_score"] == 7.5

    def test_not_completed_returns_400(self, client):
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "IN_PROGRESS",
            "title": "Not Done",
            "target_questions": 8,
            "current_question_number": 1,
            "current_difficulty": 5.0,
            "match_analysis_json": {"focus_areas": [{"topic": "T", "reason": "R"}]},
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.post(f"/interviews/{interview_id}/report")
        assert resp.status_code == 400
        assert "COMPLETED" in resp.json()["detail"]

    def test_nonexistent_interview(self, client):
        resp = client.post(f"/interviews/{uuid4()}/report")
        assert resp.status_code == 404


class TestGetReport:
    def test_get_after_generate(self, client):
        interview_id = _make_completed_interview()
        client.post(f"/interviews/{interview_id}/report")
        resp = client.get(f"/interviews/{interview_id}/report")
        assert resp.status_code == 200
        data = resp.json()
        assert data["overall_score"] == 7.5

    def test_get_before_generate_returns_404(self, client):
        interview_id = _make_completed_interview()
        resp = client.get(f"/interviews/{interview_id}/report")
        assert resp.status_code == 404
        assert "not generated" in resp.json()["detail"].lower()

    def test_get_nonexistent_interview(self, client):
        resp = client.get(f"/interviews/{uuid4()}/report")
        assert resp.status_code == 404

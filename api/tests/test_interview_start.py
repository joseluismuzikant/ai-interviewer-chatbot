import pytest

from tests.conftest import FAKE_SUPABASE
from uuid import uuid4


def _make_interview_data(interview_id: str | None = None) -> str:
    uid = interview_id or str(uuid4())
    FAKE_SUPABASE._tables["interviews"].append({
        "id": uid,
        "status": "READY",
        "title": "Start Test",
        "target_questions": 8,
        "current_question_number": 0,
        "current_difficulty": 5.0,
        "match_analysis_json": {
            "role_summary": "A role",
            "candidate_summary": "A candidate",
            "focus_areas": [
                {"topic": "Python", "reason": "Core requirement"},
                {"topic": "FastAPI", "reason": "Framework used"},
            ],
            "potential_gaps": [
                {"topic": "Cloud", "reason": "Limited exposure"}
            ],
        },
        "report_json": None,
        "created_at": "2025-01-01T00:00:00",
        "updated_at": "2025-01-01T00:00:00",
    })
    return uid


class TestStartInterview:
    def test_starts_ready_interview(self, client):
        interview_id = _make_interview_data()
        resp = client.post(f"/interviews/{interview_id}/start")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["interview_id"] == interview_id
        question = data["question"]
        assert question["content"]
        assert question["topic"]
        assert question["difficulty"] == 5.0
        assert question["question_number"] == 1
        assert len(question["expected_signals"]) > 0

    def test_start_updates_interview_status(self, client):
        interview_id = _make_interview_data()
        client.post(f"/interviews/{interview_id}/start")
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["status"] == "IN_PROGRESS"
        assert interview["current_question_number"] == 1

    def test_stores_assistant_message(self, client):
        interview_id = _make_interview_data()
        client.post(f"/interviews/{interview_id}/start")
        messages = FAKE_SUPABASE._tables["messages"]
        assert len(messages) == 1
        assert messages[0]["role"] == "assistant"
        assert messages[0]["question_number"] == 1

    def test_start_in_progress_returns_existing_question(self, client):
        interview_id = _make_interview_data()
        client.post(f"/interviews/{interview_id}/start")
        resp2 = client.post(f"/interviews/{interview_id}/start")
        assert resp2.status_code == 200
        assert resp2.json()["status"] == "IN_PROGRESS"

    def test_start_draft_returns_400(self, client):
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "DRAFT",
            "title": "Draft Interview",
            "target_questions": 8,
            "current_question_number": 0,
            "current_difficulty": 5.0,
            "match_analysis_json": {
                "role_summary": "R",
                "candidate_summary": "C",
                "focus_areas": [{"topic": "T", "reason": "R"}],
                "potential_gaps": [],
            },
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.post(f"/interviews/{interview_id}/start")
        assert resp.status_code == 400
        assert "READY" in resp.json()["detail"]

    def test_start_missing_match_analysis_returns_400(self, client):
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "READY",
            "title": "No Match",
            "target_questions": 8,
            "current_question_number": 0,
            "current_difficulty": 5.0,
            "match_analysis_json": None,
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.post(f"/interviews/{interview_id}/start")
        assert resp.status_code == 400
        assert "match_analysis_json" in resp.json()["detail"]

    def test_start_nonexistent_returns_404(self, client):
        resp = client.post(f"/interviews/{uuid4()}/start")
        assert resp.status_code == 404


class TestGetMessages:
    def test_empty_messages(self, client):
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "DRAFT",
            "title": "Empty",
            "target_questions": 8,
            "current_question_number": 0,
            "current_difficulty": 5.0,
            "match_analysis_json": None,
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.get(f"/interviews/{interview_id}/messages")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_stored_messages(self, client):
        interview_id = _make_interview_data()
        client.post(f"/interviews/{interview_id}/start")
        resp = client.get(f"/interviews/{interview_id}/messages")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["role"] == "assistant"
        assert data[0]["question_number"] == 1

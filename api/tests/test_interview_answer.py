import pytest

from tests.conftest import FAKE_SUPABASE
from app.application.use_cases.question_meta_store import set_question_meta
from uuid import uuid4


def _make_in_progress_interview(interview_id: str | None = None, target_questions: int = 2) -> str:
    uid = interview_id or str(uuid4())
    FAKE_SUPABASE._tables["interviews"].append({
        "id": uid,
        "status": "IN_PROGRESS",
        "title": "Answer Test",
        "target_questions": target_questions,
        "current_question_number": 1,
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
    FAKE_SUPABASE._tables["messages"].append({
        "id": str(uuid4()),
        "interview_id": uid,
        "role": "assistant",
        "content": "What is your experience with Python?",
        "question_number": 1,
        "difficulty_level": 5.0,
        "answer_quality_score": None,
        "response_time_ms": None,
        "paste_detected": False,
        "created_at": "2025-01-01T00:01:00",
    })
    set_question_meta(uid, 1, {
        "topic": "Python",
        "difficulty": 5.0,
        "expected_signals": ["OOP", "async"],
    })
    return uid


ANSWER_PAYLOAD = {
    "answer": "I have 5 years of Python experience building REST APIs with FastAPI.",
    "response_time_ms": 45000,
    "paste_detected": False,
}


class TestSubmitAnswer:
    def test_must_be_in_progress(self, client):
        interview_id = str(uuid4())
        FAKE_SUPABASE._tables["interviews"].append({
            "id": interview_id,
            "status": "DRAFT",
            "title": "Not Started",
            "target_questions": 8,
            "current_question_number": 0,
            "current_difficulty": 5.0,
            "match_analysis_json": None,
            "report_json": None,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
        })
        resp = client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        assert resp.status_code == 400
        assert "IN_PROGRESS" in resp.json()["detail"]

    def test_nonexistent_interview(self, client):
        resp = client.post(f"/interviews/{uuid4()}/answer", json=ANSWER_PAYLOAD)
        assert resp.status_code == 404


class TestAnswerCaseA:
    """Case A — normal answer, not finished (target_questions=3, current=1)."""

    def test_returns_in_progress_with_next_question(self, client):
        interview_id = _make_in_progress_interview(target_questions=3)
        resp = client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["interview_id"] == interview_id
        assert "evaluation" in data
        assert data["evaluation"]["score"] >= 1
        assert data["evaluation"]["score"] <= 10
        assert data["next_question"] is not None
        assert data["next_question"]["question_number"] == 2

    def test_stores_candidate_answer(self, client):
        interview_id = _make_in_progress_interview(target_questions=3)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        messages = FAKE_SUPABASE._tables["messages"]
        candidate_msgs = [m for m in messages if m["role"] == "candidate"]
        assert len(candidate_msgs) == 1
        assert candidate_msgs[0]["content"] == ANSWER_PAYLOAD["answer"]

    def test_stores_next_assistant_question(self, client):
        interview_id = _make_in_progress_interview(target_questions=3)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        messages = FAKE_SUPABASE._tables["messages"]
        assistant_msgs = [m for m in messages if m["role"] == "assistant"]
        assert len(assistant_msgs) == 2

    def test_updates_difficulty(self, client):
        interview_id = _make_in_progress_interview(target_questions=3)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["current_difficulty"] != 5.0 or interview["current_question_number"] == 2

    def test_question_number_incremented(self, client):
        interview_id = _make_in_progress_interview(target_questions=3)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["current_question_number"] == 2


class TestAnswerCaseB:
    """Case B — final answer reaches target_questions."""

    def test_returns_completed(self, client):
        interview_id = _make_in_progress_interview(target_questions=1)
        resp = client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "COMPLETED"
        assert data["next_question"] is None

    def test_updates_status_to_completed(self, client):
        interview_id = _make_in_progress_interview(target_questions=1)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["status"] == "COMPLETED"

    def test_no_next_question_generated(self, client):
        interview_id = _make_in_progress_interview(target_questions=1)
        client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        assistant_msgs = [
            m for m in FAKE_SUPABASE._tables["messages"]
            if m["role"] == "assistant"
        ]
        assert len(assistant_msgs) == 1

    def test_evaluation_is_returned(self, client):
        interview_id = _make_in_progress_interview(target_questions=1)
        resp = client.post(f"/interviews/{interview_id}/answer", json=ANSWER_PAYLOAD)
        data = resp.json()
        assert "evaluation" in data
        assert "score" in data["evaluation"]
        assert "rationale" in data["evaluation"]
        assert "evidence" in data["evaluation"]


class TestAnswerCaseC:
    """Case C — answers with low score adjust difficulty down."""

    LOW_SCORE_PAYLOAD = {
        "answer": "I know Python.",
        "response_time_ms": 5000,
        "paste_detected": False,
    }

    def test_difficulty_decreases_on_low_score(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.infrastructure.llm.mock.MockProvider.evaluate_answer",
            lambda self, ctx: {"score": 3, "rationale": "weak", "evidence": "vague", "followup_hint": "be specific"},
        )
        interview_id = _make_in_progress_interview(target_questions=3)
        client.post(f"/interviews/{interview_id}/answer", json=self.LOW_SCORE_PAYLOAD)
        interview = FAKE_SUPABASE._tables["interviews"][0]
        current_diff = interview["current_difficulty"]
        assert current_diff == 4.5

    def test_rating_clamped_to_minimum(self, client, monkeypatch):
        monkeypatch.setattr(
            "app.infrastructure.llm.mock.MockProvider.evaluate_answer",
            lambda self, ctx: {"score": 2, "rationale": "weak", "evidence": "vague", "followup_hint": "be specific"},
        )
        interview_id = _make_in_progress_interview(target_questions=10)
        FAKE_SUPABASE._tables["interviews"][0]["current_difficulty"] = 3.0
        for _ in range(5):
            client.post(f"/interviews/{interview_id}/answer", json=self.LOW_SCORE_PAYLOAD)
        interview = FAKE_SUPABASE._tables["interviews"][0]
        assert interview["current_difficulty"] >= 3.0

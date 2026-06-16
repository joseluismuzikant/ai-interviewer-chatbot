from uuid import uuid4

import pytest


def _create_interview(client, title="Test Interview", target_questions=8, starting_difficulty=5):
    return client.post(
        "/interviews",
        json={
            "title": title,
            "target_questions": target_questions,
            "starting_difficulty": starting_difficulty,
        },
    )


class TestCreateInterview:
    def test_creates_interview(self, client):
        resp = _create_interview(client)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "DRAFT"
        assert data["title"] == "Test Interview"
        assert data["target_questions"] == 8
        assert data["current_difficulty"] == 5
        assert data["current_question_number"] == 0
        assert "id" in data

    def test_default_values(self, client):
        resp = client.post("/interviews", json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] is None
        assert data["target_questions"] == 8
        assert data["current_difficulty"] == 5

    def test_custom_difficulty(self, client):
        resp = _create_interview(client, starting_difficulty=7)
        assert resp.status_code == 200
        assert resp.json()["current_difficulty"] == 7


class TestListInterviews:
    def test_empty_list(self, client):
        resp = client.get("/interviews")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_created_interviews(self, client):
        _create_interview(client, title="First")
        _create_interview(client, title="Second")
        resp = client.get("/interviews")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        titles = [i["title"] for i in data]
        assert "First" in titles
        assert "Second" in titles


class TestGetInterview:
    def test_returns_interview(self, client):
        create_resp = _create_interview(client)
        interview_id = create_resp.json()["id"]
        resp = client.get(f"/interviews/{interview_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == interview_id

    def test_404_for_nonexistent(self, client):
        resp = client.get(f"/interviews/{uuid4()}")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Interview not found"


class TestDeleteInterview:
    def test_deletes_existing(self, client):
        create_resp = _create_interview(client)
        interview_id = create_resp.json()["id"]
        resp = client.delete(f"/interviews/{interview_id}")
        assert resp.status_code == 204

    def test_cannot_get_after_delete(self, client):
        create_resp = _create_interview(client)
        interview_id = create_resp.json()["id"]
        client.delete(f"/interviews/{interview_id}")
        resp = client.get(f"/interviews/{interview_id}")
        assert resp.status_code == 404

    def test_404_for_nonexistent_delete(self, client):
        resp = client.delete(f"/interviews/{uuid4()}")
        assert resp.status_code == 404

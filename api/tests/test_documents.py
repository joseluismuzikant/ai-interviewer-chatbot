from uuid import uuid4

import pytest

from tests.conftest import FAKE_SUPABASE, reset_fake_supabase
from app.application.use_cases.document_service import DocumentService


def _create_interview(client):
    resp = client.post("/interviews", json={"title": "Doc Test"})
    return resp.json()["id"]


FAKE_PDF_CONTENT = b"%PDF-1.4 fake pdf content for testing"


def _upload_document(client, interview_id, doc_type="resume"):
    return client.post(
        f"/interviews/{interview_id}/documents",
        data={"document_type": doc_type},
        files={"file": ("resume.pdf", FAKE_PDF_CONTENT, "application/pdf")},
    )


class TestDocumentUpload:
    def test_upload_resume(self, client, monkeypatch):
        monkeypatch.setattr(DocumentService, "_extract_text_from_pdf", lambda self, fb: "extracted resume text")
        interview_id = _create_interview(client)
        resp = _upload_document(client, interview_id, "resume")
        assert resp.status_code == 200
        data = resp.json()
        assert data["document_type"] == "resume"
        assert data["interview_id"] == interview_id
        assert data["extracted_character_count"] > 0
        assert "storage_path" in data

    def test_upload_role_description(self, client, monkeypatch):
        monkeypatch.setattr(DocumentService, "_extract_text_from_pdf", lambda self, fb: "extracted role text")
        interview_id = _create_interview(client)
        resp = _upload_document(client, interview_id, "role_description")
        assert resp.status_code == 200
        assert resp.json()["document_type"] == "role_description"

    def test_upload_replaces_existing_type(self, client, monkeypatch):
        monkeypatch.setattr(DocumentService, "_extract_text_from_pdf", lambda self, fb: "extracted text")
        interview_id = _create_interview(client)
        _upload_document(client, interview_id, "resume")
        resp2 = _upload_document(client, interview_id, "resume")
        assert resp2.status_code == 200

    def test_upload_non_pdf_fails(self, client):
        interview_id = _create_interview(client)
        resp = client.post(
            f"/interviews/{interview_id}/documents",
            data={"document_type": "resume"},
            files={"file": ("test.txt", b"not a pdf", "text/plain")},
        )
        assert resp.status_code == 400
        assert "PDF" in resp.json()["detail"]

    def test_upload_invalid_document_type(self, client):
        interview_id = _create_interview(client)
        resp = client.post(
            f"/interviews/{interview_id}/documents",
            data={"document_type": "invalid"},
            files={"file": ("test.pdf", FAKE_PDF_CONTENT, "application/pdf")},
        )
        assert resp.status_code == 422

    def test_upload_nonexistent_interview(self, client):
        resp = client.post(
            f"/interviews/{uuid4()}/documents",
            data={"document_type": "resume"},
            files={"file": ("test.pdf", FAKE_PDF_CONTENT, "application/pdf")},
        )
        assert resp.status_code == 404


class TestListDocuments:
    def test_empty_list(self, client):
        interview_id = _create_interview(client)
        resp = client.get(f"/interviews/{interview_id}/documents")
        assert resp.status_code == 200
        assert resp.json()["documents"] == []

    def test_returns_uploaded_documents(self, client, monkeypatch):
        monkeypatch.setattr(DocumentService, "_extract_text_from_pdf", lambda self, fb: "extracted text")
        interview_id = _create_interview(client)
        _upload_document(client, interview_id, "resume")
        _upload_document(client, interview_id, "role_description")
        resp = client.get(f"/interviews/{interview_id}/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["documents"]) == 2
        types = [d["document_type"] for d in data["documents"]]
        assert "resume" in types
        assert "role_description" in types

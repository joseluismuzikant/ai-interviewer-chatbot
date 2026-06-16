from uuid import UUID

import pytest
from pydantic import ValidationError

from app.presentation.schemas.health import HealthResponse
from app.presentation.schemas.interview import InterviewCreateRequest, InterviewResponse
from app.presentation.schemas.analysis import FocusArea, PotentialGap, MatchAnalysis
from app.presentation.schemas.question import InterviewQuestion, StartedQuestion, InterviewStartResponse
from app.presentation.schemas.answer import AnswerRequest, AnswerEvaluation, InterviewAnswerResponse
from app.presentation.schemas.report import GeneratedReport, FinalReportResponse
from app.presentation.schemas.document import DocumentUploadResponse, DocumentRecord, DocumentListResponse
from app.presentation.schemas.message import MessageResponse


class TestHealthResponse:
    def test_valid(self):
        r = HealthResponse(status="ok")
        assert r.status == "ok"

    def test_serializes(self):
        assert HealthResponse(status="ok").model_dump() == {"status": "ok"}


class TestInterviewCreateRequest:
    def test_defaults(self):
        r = InterviewCreateRequest()
        assert r.title is None
        assert r.target_questions == 8
        assert r.starting_difficulty == 5

    def test_custom_values(self):
        r = InterviewCreateRequest(title="Test", target_questions=10, starting_difficulty=7)
        assert r.title == "Test"
        assert r.target_questions == 10
        assert r.starting_difficulty == 7

    def test_target_questions_clamped(self):
        with pytest.raises(ValidationError):
            InterviewCreateRequest(target_questions=0)

    def test_starting_difficulty_clamped(self):
        with pytest.raises(ValidationError):
            InterviewCreateRequest(starting_difficulty=1)


class TestInterviewResponse:
    def test_valid(self):
        r = InterviewResponse(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            status="DRAFT",
            target_questions=8,
            current_question_number=0,
            current_difficulty=5.0,
        )
        assert r.status == "DRAFT"
        assert r.title is None

    def test_with_all_fields(self):
        r = InterviewResponse(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            status="READY",
            title="Test",
            target_questions=5,
            current_question_number=0,
            current_difficulty=5.0,
            match_analysis_json={"role_summary": "..."},
            report_json={"summary": "..."},
        )
        assert r.match_analysis_json == {"role_summary": "..."}
        assert r.report_json == {"summary": "..."}


class TestAnalysisSchemas:
    def test_focus_area(self):
        fa = FocusArea(topic="Python", reason="Core skill")
        assert fa.topic == "Python"
        assert fa.reason == "Core skill"

    def test_focus_area_forbid_extra(self):
        with pytest.raises(ValidationError):
            FocusArea(topic="Python", reason="Core skill", extra="forbidden")

    def test_potential_gap(self):
        pg = PotentialGap(topic="Cloud", reason="Limited exposure")
        assert pg.topic == "Cloud"

    def test_match_analysis(self):
        ma = MatchAnalysis(
            role_summary="Senior Engineer",
            candidate_summary="Experienced",
            focus_areas=[FocusArea(topic="Python", reason="Core skill")],
            potential_gaps=[PotentialGap(topic="Cloud", reason="Limited exposure")],
        )
        assert len(ma.focus_areas) == 1
        assert len(ma.potential_gaps) == 1


class TestInterviewQuestion:
    def test_valid(self):
        q = InterviewQuestion(
            question="What is Python?",
            topic="Python",
            difficulty=5,
            expected_signals=["OOP", "typing"],
        )
        assert q.question == "What is Python?"

    def test_forbid_extra(self):
        with pytest.raises(ValidationError):
            InterviewQuestion(
                question="Q",
                topic="T",
                difficulty=5,
                expected_signals=["s"],
                extra="x",
            )


class TestStartedQuestion:
    def test_valid(self):
        q = StartedQuestion(
            content="What is Python?",
            topic="Python",
            difficulty=5.0,
            question_number=1,
            expected_signals=["OOP"],
        )
        assert q.id is None
        assert q.content == "What is Python?"

    def test_with_id(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        q = StartedQuestion(
            id=uid,
            content="C",
            topic="T",
            difficulty=5.0,
            question_number=1,
            expected_signals=["s"],
        )
        assert q.id == uid


class TestInterviewStartResponse:
    def test_valid(self):
        q = StartedQuestion(
            content="Q", topic="T", difficulty=5.0, question_number=1, expected_signals=["s"]
        )
        r = InterviewStartResponse(
            interview_id=UUID("00000000-0000-0000-0000-000000000001"),
            status="IN_PROGRESS",
            question=q,
        )
        assert r.status == "IN_PROGRESS"


class TestAnswerRequest:
    def test_valid(self):
        r = AnswerRequest(answer="My answer", response_time_ms=45000, paste_detected=False)
        assert r.answer == "My answer"

    def test_empty_answer_fails(self):
        with pytest.raises(ValidationError):
            AnswerRequest(answer="", response_time_ms=1000, paste_detected=False)

    def test_negative_time_fails(self):
        with pytest.raises(ValidationError):
            AnswerRequest(answer="a", response_time_ms=-1, paste_detected=False)

    def test_forbid_extra(self):
        with pytest.raises(ValidationError):
            AnswerRequest(answer="a", response_time_ms=1000, paste_detected=False, extra="x")


class TestAnswerEvaluation:
    def test_valid(self):
        e = AnswerEvaluation(score=7, rationale="Good", evidence="Clear", followup_hint="Deeper")
        assert e.score == 7

    def test_score_out_of_range(self):
        with pytest.raises(ValidationError):
            AnswerEvaluation(score=11, rationale="R", evidence="E", followup_hint="H")

    def test_score_min(self):
        with pytest.raises(ValidationError):
            AnswerEvaluation(score=0, rationale="R", evidence="E", followup_hint="H")


class TestInterviewAnswerResponse:
    def test_in_progress(self):
        q = StartedQuestion(
            content="Q", topic="T", difficulty=5.0, question_number=2, expected_signals=["s"]
        )
        e = AnswerEvaluation(score=7, rationale="Good", evidence="Clear", followup_hint="Deeper")
        r = InterviewAnswerResponse(
            interview_id=UUID("00000000-0000-0000-0000-000000000001"),
            status="IN_PROGRESS",
            evaluation=e,
            next_question=q,
        )
        assert r.status == "IN_PROGRESS"
        assert r.next_question is not None

    def test_completed(self):
        e = AnswerEvaluation(score=7, rationale="Good", evidence="Clear", followup_hint="Deeper")
        r = InterviewAnswerResponse(
            interview_id=UUID("00000000-0000-0000-0000-000000000001"),
            status="COMPLETED",
            evaluation=e,
            next_question=None,
        )
        assert r.status == "COMPLETED"
        assert r.next_question is None


class TestGeneratedReport:
    def test_valid(self):
        r = GeneratedReport(
            summary="Good candidate",
            strengths=["Python"],
            weaknesses=["Cloud"],
            recommendation="YES",
            recommendation_rationale="Strong fit",
        )
        assert r.recommendation == "YES"

    def test_invalid_recommendation(self):
        with pytest.raises(ValidationError):
            GeneratedReport(
                summary="S",
                strengths=[],
                weaknesses=[],
                recommendation="MAYBE",
                recommendation_rationale="R",
            )


class TestFinalReportResponse:
    def test_valid(self):
        r = FinalReportResponse(
            summary="Good candidate",
            overall_score=7.5,
            strengths=["Python"],
            weaknesses=["Cloud"],
            integrity_notes=[],
            recommendation="MIXED",
            recommendation_rationale="Balanced",
        )
        assert r.overall_score == 7.5

    def test_score_bounds(self):
        with pytest.raises(ValidationError):
            FinalReportResponse(
                summary="S",
                overall_score=11,
                strengths=[],
                weaknesses=[],
                integrity_notes=[],
                recommendation="NO",
                recommendation_rationale="R",
            )


class TestDocumentSchemas:
    def test_document_upload_response(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        r = DocumentUploadResponse(
            interview_id=uid,
            document_type="resume",
            extracted_character_count=100,
            storage_path="path/to/file.pdf",
        )
        assert r.document_type == "resume"

    def test_document_record(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        r = DocumentRecord(
            id=uid,
            interview_id=uid,
            document_type="role_description",
            filename="role.pdf",
            storage_path="path/to/role.pdf",
            extracted_character_count=200,
        )
        assert r.filename == "role.pdf"

    def test_document_list_response(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        doc = DocumentRecord(
            id=uid,
            interview_id=uid,
            document_type="resume",
            filename="resume.pdf",
            storage_path="path",
            extracted_character_count=100,
        )
        r = DocumentListResponse(interview_id=uid, documents=[doc])
        assert len(r.documents) == 1


class TestMessageResponse:
    def test_valid(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        m = MessageResponse(
            id=uid,
            interview_id=uid,
            role="assistant",
            content="Hello",
        )
        assert m.content == "Hello"

    def test_with_all_fields(self):
        uid = UUID("00000000-0000-0000-0000-000000000001")
        m = MessageResponse(
            id=uid,
            interview_id=uid,
            role="candidate",
            content="Answer",
            question_number=1,
            difficulty_level=5.0,
            answer_quality_score=7,
            response_time_ms=30000,
            paste_detected=False,
        )
        assert m.answer_quality_score == 7

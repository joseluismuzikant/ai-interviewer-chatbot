from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.application.use_cases.analysis_service import AnalysisService
from app.application.use_cases.document_service import DocumentService
from app.application.use_cases.interview_answer_service import InterviewAnswerService
from app.application.use_cases.interview_service import InterviewService
from app.application.use_cases.interview_start_service import InterviewStartService
from app.application.use_cases.report_service import ReportService
from app.presentation.dependencies import (
    get_analysis_service,
    get_document_service,
    get_interview_answer_service,
    get_interview_service,
    get_interview_start_service,
    get_report_service,
)
from app.presentation.schemas.answer import AnswerRequest, InterviewAnswerResponse
from app.presentation.schemas.document import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentRecord,
    DocumentStorageListResponse,
    DocumentUploadResponse,
)
from app.presentation.schemas.interview import InterviewCreateRequest, InterviewResponse
from app.presentation.schemas.message import MessageResponse
from app.presentation.schemas.analysis import MatchAnalysis
from app.presentation.schemas.question import InterviewStartResponse
from app.presentation.schemas.report import FinalReportResponse

router = APIRouter(tags=["interviews"])


@router.post("/interviews", response_model=InterviewResponse)
def create_interview(
    payload: InterviewCreateRequest,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.create_interview(payload)
    return InterviewResponse(**interview)


@router.get("/interviews", response_model=list[InterviewResponse])
def list_interviews(
    interview_service: InterviewService = Depends(get_interview_service),
) -> list[InterviewResponse]:
    interviews = interview_service.list_interviews()
    return [InterviewResponse(**interview) for interview in interviews]


@router.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.get_interview(interview_id)
    return InterviewResponse(**interview)


@router.delete("/interviews/{interview_id}", status_code=204)
def delete_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> None:
    interview_service.delete_interview(interview_id)


@router.post("/interviews/{interview_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    interview_id: UUID,
    document_type: Literal["resume", "role_description"] = Form(...),
    file: UploadFile = File(...),
    interview_service: InterviewService = Depends(get_interview_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    interview_service.get_interview(interview_id)

    file_bytes = await file.read()
    upload_result = document_service.process_document(
        interview_id=interview_id,
        document_type=document_type,
        filename=file.filename or "document.pdf",
        content_type=file.content_type,
        file_bytes=file_bytes,
    )
    return DocumentUploadResponse(**upload_result)


@router.get("/interviews/{interview_id}/documents", response_model=DocumentListResponse)
def list_documents(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    interview_service.get_interview(interview_id)
    documents = document_service.list_documents_from_table(interview_id)
    return DocumentListResponse(
        interview_id=interview_id,
        documents=[DocumentRecord(**document) for document in documents],
    )


@router.get(
    "/interviews/{interview_id}/documentsFromStorage",
    response_model=DocumentStorageListResponse,
)
def list_documents_from_storage(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentStorageListResponse:
    interview_service.get_interview(interview_id)
    document_names = document_service.list_document_names(interview_id)
    return DocumentStorageListResponse(
        interview_id=interview_id,
        documents=document_names,
    )


@router.delete(
    "/interviews/{interview_id}/documents/{filename:path}",
    response_model=DocumentDeleteResponse,
)
def delete_document(
    interview_id: UUID,
    filename: str,
    interview_service: InterviewService = Depends(get_interview_service),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentDeleteResponse:
    interview_service.get_interview(interview_id)
    deleted = document_service.delete_document(
        interview_id=interview_id, filename=filename
    )
    return DocumentDeleteResponse(**deleted)


@router.post(
    "/interviews/{interview_id}/analyze",
    response_model=MatchAnalysis,
)
def analyze_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> MatchAnalysis:
    interview_service.get_interview(interview_id)
    result = analysis_service.analyze_interview(interview_id)
    return MatchAnalysis(**result)


@router.post(
    "/interviews/{interview_id}/start",
    response_model=InterviewStartResponse,
)
def start_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    interview_start_service: InterviewStartService = Depends(get_interview_start_service),
) -> InterviewStartResponse:
    interview = interview_service.get_interview(interview_id)
    return interview_start_service.start_interview(interview)


@router.get("/interviews/{interview_id}/messages", response_model=list[MessageResponse])
def get_interview_messages(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> list[MessageResponse]:
    interview_service.get_interview(interview_id)
    messages = interview_service.list_messages(interview_id)
    return [MessageResponse(**message) for message in messages]


@router.post(
    "/interviews/{interview_id}/answer",
    response_model=InterviewAnswerResponse,
)
def submit_answer(
    interview_id: UUID,
    payload: AnswerRequest,
    interview_service: InterviewService = Depends(get_interview_service),
    interview_answer_service: InterviewAnswerService = Depends(get_interview_answer_service),
) -> InterviewAnswerResponse:
    interview = interview_service.get_interview(interview_id)
    return interview_answer_service.submit_answer(interview, payload)


@router.post(
    "/interviews/{interview_id}/report",
    response_model=FinalReportResponse,
)
def generate_interview_report(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    report_service: ReportService = Depends(get_report_service),
) -> FinalReportResponse:
    interview = interview_service.get_interview(interview_id)
    return report_service.generate_report(interview)


@router.get(
    "/interviews/{interview_id}/report",
    response_model=FinalReportResponse,
)
def get_interview_report(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    report_service: ReportService = Depends(get_report_service),
) -> FinalReportResponse:
    interview = interview_service.get_interview(interview_id)
    return report_service.get_report(interview)

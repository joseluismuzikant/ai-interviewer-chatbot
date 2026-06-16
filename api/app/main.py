from functools import lru_cache
from typing import Literal
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.analysis_service import AnalysisService
from app.config import get_settings
from app.document_service import DocumentService
from app.interview_answer_service import InterviewAnswerService
from app.interview_start_service import InterviewStartService
from app.interview_service import InterviewService
from app.llm import get_llm_client
from app.report_service import ReportService
from app.schemas import (
    AnswerRequest,
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentRecord,
    DocumentStorageListResponse,
    DocumentUploadResponse,
    FinalReportResponse,
    HealthResponse,
    InterviewAnswerResponse,
    InterviewCreateRequest,
    InterviewStartResponse,
    InterviewResponse,
    MessageResponse,
    MatchAnalysis,
)
from app.supabase_client import get_supabase_client

settings = get_settings()

app = FastAPI(title=settings.app_name, debug=settings.app_debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")


@lru_cache
def get_cached_supabase_client():
    settings = get_settings()
    try:
        return get_supabase_client(settings)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def get_interview_service() -> InterviewService:
    return InterviewService(supabase=get_cached_supabase_client())


@lru_cache
def get_cached_document_service() -> DocumentService:
    return DocumentService(supabase=get_cached_supabase_client())


def get_document_service() -> DocumentService:
    return get_cached_document_service()


@lru_cache
def get_cached_llm_client():
    return get_llm_client(get_settings())


def get_llm_client_instance():
    return get_cached_llm_client()


def get_analysis_service() -> AnalysisService:
    return AnalysisService(
        supabase=get_cached_supabase_client(),
        llm=get_cached_llm_client(),
    )


@lru_cache
def get_interview_start_service() -> InterviewStartService:
    return InterviewStartService(
        supabase=get_cached_supabase_client(),
        llm=get_cached_llm_client(),
    )


@lru_cache
def get_interview_answer_service() -> InterviewAnswerService:
    return InterviewAnswerService(
        supabase=get_cached_supabase_client(),
        llm=get_cached_llm_client(),
    )


@lru_cache
def get_report_service() -> ReportService:
    return ReportService(
        supabase=get_cached_supabase_client(),
        llm=get_cached_llm_client(),
    )


@app.post("/interviews", response_model=InterviewResponse)
def create_interview(
    payload: InterviewCreateRequest,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.create_interview(payload)
    return InterviewResponse(**interview)


@app.get("/interviews", response_model=list[InterviewResponse])
def list_interviews(
    interview_service: InterviewService = Depends(get_interview_service),
) -> list[InterviewResponse]:
    interviews = interview_service.list_interviews()
    return [InterviewResponse(**interview) for interview in interviews]


@app.get("/interviews/{interview_id}", response_model=InterviewResponse)
def get_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> InterviewResponse:
    interview = interview_service.get_interview(interview_id)
    return InterviewResponse(**interview)


@app.delete("/interviews/{interview_id}", status_code=204)
def delete_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> None:
    interview_service.delete_interview(interview_id)


@app.post("/interviews/{interview_id}/documents", response_model=DocumentUploadResponse)
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


@app.get("/interviews/{interview_id}/documents", response_model=DocumentListResponse)
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


@app.get(
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


@app.delete(
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


@app.post(
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


@app.post(
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


@app.get("/interviews/{interview_id}/messages", response_model=list[MessageResponse])
def get_interview_messages(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
) -> list[MessageResponse]:
    interview_service.get_interview(interview_id)
    messages = interview_service.list_messages(interview_id)
    return [MessageResponse(**message) for message in messages]


@app.post(
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


@app.post(
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


@app.get(
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

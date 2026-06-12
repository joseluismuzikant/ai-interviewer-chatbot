from functools import lru_cache
from typing import Literal
from uuid import UUID

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.analysis_service import AnalysisService
from app.config import get_settings
from app.document_service import DocumentService
from app.interview_service import InterviewService
from app.llm import get_llm_client
from app.schemas import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentRecord,
    DocumentStorageListResponse,
    DocumentUploadResponse,
    HealthResponse,
    InterviewCreateRequest,
    InterviewResponse,
    MatchAnalysisResponse,
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
    response_model=MatchAnalysisResponse,
)
def analyze_interview(
    interview_id: UUID,
    interview_service: InterviewService = Depends(get_interview_service),
    analysis_service: AnalysisService = Depends(get_analysis_service),
) -> MatchAnalysisResponse:
    interview_service.get_interview(interview_id)
    result = analysis_service.analyze_interview(interview_id)
    return MatchAnalysisResponse(**result)

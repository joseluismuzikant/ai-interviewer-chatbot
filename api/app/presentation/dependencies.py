from functools import lru_cache

from fastapi import HTTPException

from app.application.use_cases.analysis_service import AnalysisService
from app.application.use_cases.document_service import DocumentService
from app.application.use_cases.interview_answer_service import InterviewAnswerService
from app.application.use_cases.interview_service import InterviewService
from app.application.use_cases.interview_start_service import InterviewStartService
from app.application.use_cases.report_service import ReportService
from app.core.config import get_settings
from app.core.llm import get_llm_client
from app.infrastructure.data.supabase_client import get_supabase_client


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

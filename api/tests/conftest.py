import os

os.environ["SUPABASE_URL"] = "http://localhost:54321"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["SUPABASE_STORAGE_BUCKET"] = "test-bucket"
os.environ["LLM_PROVIDER"] = "mock"
os.environ["OPENAI_API_KEY"] = "test-openai-key"
os.environ["OPENAI_MODEL"] = "gpt-4o-mini"
os.environ["GOOGLE_API_KEY"] = "test-google-key"
os.environ["GOOGLE_MODEL"] = "gemini-2.0-flash"
os.environ["DEEPSEEK_API_KEY"] = "test-deepseek-key"
os.environ["DEEPSEEK_MODEL"] = "deepseek-chat"

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


def uuid_str() -> str:
    return str(uuid4())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FakeResponse:
    def __init__(self, data: list[dict]):
        self.data = data


class FakeStorageBucket:
    def __init__(self, files: dict[str, bytes]):
        self._files = files

    def upload(self, path: str, file: bytes, file_options: dict | None = None) -> None:
        self._files[path] = file if isinstance(file, bytes) else str(file).encode()

    def list(self, path: str):
        return []

    def remove(self, paths):
        for p in paths:
            self._files.pop(p, None)


class FakeStorageWrapper:
    def __init__(self, files):
        self._files = files

    def from_(self, bucket_name: str):
        return FakeStorageBucket(self._files)


_TABLE_DEFAULTS: dict[str, dict[str, object]] = {
    "interviews": {
        "status": "DRAFT",
        "current_question_number": 0,
    },
}


class FakeQuery:
    def __init__(self, table_name: str, table_data: list[dict]):
        self._table_name = table_name
        self._data = table_data
        self._filters: dict[str, Any] = {}
        self._limit_val: int | None = None
        self._order_col: str | None = None
        self._order_desc: bool = False
        self._delete_mode: bool = False
        self._update_data: dict | None = None
        self._insert_data: dict | None = None
        self._upsert_data: dict | None = None
        self._on_conflict: str | None = None
        self._select_cols: str = "*"

    def select(self, cols: str = "*"):
        self._select_cols = cols
        return self

    def eq(self, key: str, value: Any):
        self._filters[key] = value
        return self

    def limit(self, n: int):
        self._limit_val = n
        return self

    def order(self, col: str, desc: bool = False):
        self._order_col = col
        self._order_desc = desc
        return self

    def insert(self, data: dict):
        self._insert_data = data
        return self

    def upsert(self, data: dict, on_conflict: str | None = None):
        self._upsert_data = data
        self._on_conflict = on_conflict
        return self

    def update(self, data: dict):
        self._update_data = data
        return self

    def delete(self):
        self._delete_mode = True
        return self

    def _matches(self, item: dict) -> bool:
        for k, v in self._filters.items():
            if k not in item:
                return False
            if item[k] != v:
                return False
        return True

    def execute(self):
        if self._insert_data is not None:
            return self._do_insert()
        if self._upsert_data is not None:
            return self._do_upsert()
        if self._delete_mode:
            return self._do_delete()
        if self._update_data is not None:
            return self._do_update()
        return self._do_select()

    def _do_insert(self):
        item = dict(self._insert_data) if self._insert_data else {}
        table_defaults = _TABLE_DEFAULTS.get(self._table_name, {})
        for k, v in table_defaults.items():
            if k not in item:
                item[k] = v
        if "id" not in item:
            item["id"] = uuid_str()
        if "created_at" not in item:
            item["created_at"] = now_iso()
        if "updated_at" not in item:
            item["updated_at"] = now_iso()
        self._data.append(item)
        return FakeResponse([item])

    def _do_upsert(self):
        if self._upsert_data is None:
            return FakeResponse([])
        if not self._on_conflict:
            self._insert_data = dict(self._upsert_data)
            self._upsert_data = None
            return self._do_insert()
        conflict_cols = [c.strip() for c in self._on_conflict.split(",")]
        existing = None
        for item in self._data:
            match = True
            for col in conflict_cols:
                if item.get(col) != self._upsert_data.get(col):
                    match = False
                    break
            if match:
                existing = item
                break
        if existing is not None:
            existing.update(self._upsert_data)
            self._upsert_data = None
            return FakeResponse([existing])
        self._insert_data = dict(self._upsert_data)
        self._upsert_data = None
        return self._do_insert()

    def _do_update(self):
        items = [item for item in self._data if self._matches(item)]
        for item in items:
            if self._update_data:
                item.update(self._update_data)
        if "updated_at" not in (self._update_data or {}):
            for item in items:
                item["updated_at"] = now_iso()
        return FakeResponse(items)

    def _do_delete(self):
        to_keep = [item for item in self._data if not self._matches(item)]
        deleted = [item for item in self._data if self._matches(item)]
        self._data.clear()
        self._data.extend(to_keep)
        return FakeResponse(deleted)

    def _do_select(self):
        items = list(self._data)
        for k, v in self._filters.items():
            items = [i for i in items if i.get(k) == v]
        if self._order_col:
            items.sort(key=lambda i: i.get(self._order_col, ""), reverse=self._order_desc)
        if self._limit_val is not None:
            items = items[: self._limit_val]
        return FakeResponse(items)


class FakeSupabaseClient:
    def __init__(self):
        self._tables: dict[str, list[dict]] = {
            "interviews": [],
            "messages": [],
            "documents": [],
        }
        self._storage_files: dict[str, bytes] = {}

    def table(self, name: str):
        if name not in self._tables:
            self._tables[name] = []
        return FakeQuery(name, self._tables[name])

    @property
    def storage(self):
        return FakeStorageWrapper(self._storage_files)


FAKE_SUPABASE = FakeSupabaseClient()


def reset_fake_supabase():
    for table in FAKE_SUPABASE._tables.values():
        table.clear()
    FAKE_SUPABASE._storage_files.clear()


@pytest.fixture(autouse=True)
def _mock_external_services(monkeypatch):
    reset_fake_supabase()

    from app.presentation import dependencies as deps
    from app.core.config import get_settings

    get_settings.cache_clear()
    deps.get_cached_supabase_client.cache_clear()
    deps.get_cached_llm_client.cache_clear()
    deps.get_cached_document_service.cache_clear()
    deps.get_interview_start_service.cache_clear()
    deps.get_interview_answer_service.cache_clear()
    deps.get_report_service.cache_clear()

    from app.application.use_cases import question_meta_store as qms
    qms._QUESTION_META_CACHE.clear()

    app.dependency_overrides.clear()
    from app.application.use_cases.interview_service import InterviewService
    from app.application.use_cases.document_service import DocumentService
    from app.application.use_cases.analysis_service import AnalysisService
    from app.application.use_cases.interview_start_service import InterviewStartService
    from app.application.use_cases.interview_answer_service import InterviewAnswerService
    from app.application.use_cases.report_service import ReportService
    from app.core.llm import get_llm_client
    from app.core.config import get_settings

    _settings = get_settings()
    _llm = get_llm_client(_settings)

    app.dependency_overrides[deps.get_interview_service] = lambda: InterviewService(supabase=FAKE_SUPABASE)
    app.dependency_overrides[deps.get_document_service] = lambda: DocumentService(supabase=FAKE_SUPABASE)
    app.dependency_overrides[deps.get_analysis_service] = lambda: AnalysisService(supabase=FAKE_SUPABASE, llm=_llm)
    app.dependency_overrides[deps.get_interview_start_service] = lambda: InterviewStartService(supabase=FAKE_SUPABASE, llm=_llm)
    app.dependency_overrides[deps.get_interview_answer_service] = lambda: InterviewAnswerService(supabase=FAKE_SUPABASE, llm=_llm)
    app.dependency_overrides[deps.get_report_service] = lambda: ReportService(supabase=FAKE_SUPABASE, llm=_llm)

    yield


@pytest.fixture
def client():
    return TestClient(app)

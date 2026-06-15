from typing import Any

_QUESTION_META_CACHE: dict[str, dict[str, Any]] = {}


def set_question_meta(interview_id: str, question_number: int, meta: dict[str, Any]) -> None:
    key = f"{interview_id}:{question_number}"
    _QUESTION_META_CACHE[key] = meta


def get_question_meta(interview_id: str, question_number: int) -> dict[str, Any] | None:
    key = f"{interview_id}:{question_number}"
    return _QUESTION_META_CACHE.get(key)
